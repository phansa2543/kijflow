from collections.abc import Callable
from starlette.concurrency import run_in_threadpool

from fastapi import Request, HTTPException
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from starlette.responses import Response

from app.auth.application.errors import (
    RegistrationRateLimited,
    RegistrationLimiterUnavailable,
)
from app.auth.infrastructure.registration_wiring import (
    make_registration_limit_checker,
)
from app.auth.presentation.client_ip import (
    resolve_direct_client_ip,
)

MAX_REGISTRATION_BODY_BYTES = 8_192

class RegistrationBodyTooLarge(HTTPException):
    def __init__(self):
        super().__innit__(
            status_code=413,
            detail="Request body too large"
        )

class RegistrationLimitRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> Callable[[Request], Response]:

        original_handler = super().get_route_handler()

        async def limited_handler(request: Request) -> Response:
            try:
                client_ip = resolve_direct_client_ip(request)

                state = request.app.state
                engine = getattr(state, "db_engine", None)
                threshold = getattr(
                    state, "registration_rate_limit_threshold", None
                )
                window_seconds = getattr(
                    state, "registration_rate_limit_window_seconds", None
                )

                if (
                    engine is None
                    or type(threshold) is not int
                    or threshold < 1
                    or type(window_seconds) is not int
                    or window_seconds < 1
                ):
                    raise RegistrationLimiterUnavailable()

                checker = make_registration_limit_checker(
                    engine=engine,
                    client_ip=client_ip,
                    threshold=threshold,
                    window_seconds=window_seconds,
                )

                await run_in_threadpool(checker)

            except RegistrationRateLimited as exc:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "REGISTRATION_FAILED",
                            "message": "Too many requests",
                        }
                    },
                    headers={
                        "Retry-After": str(exc.retry_after_seconds),
                        "Cache-Control": "no-store",
                    },
                )

            except RegistrationLimiterUnavailable:
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": {
                            "code": "REGISTRATION_FAILED",
                            "message": "Registration temporarily unavailable",
                        }
                    },
                    headers={"Cache-Control": "no-store"},
                )

            body = bytearray()

            async for chunk in request.stream():
                if len(chunk) > MAX_REGISTRATION_BODY_BYTES - len(body):
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "REGISTRATION_FAILED",
                                "message": "Request body too large",
                            }
                        },
                        headers={"Cache-Control": "no-store"},
                    )

                body.extend(chunk)

            payload = bytes(body)
            was_sent = False


            async def replay_receive():
                nonlocal was_sent

                if not was_sent:
                    was_sent = True
                    return {
                        "type": "http.request",
                        "body": payload,
                        "more_body": False,
                    }

                return await request.receive()


            return await original_handler(
                Request(request.scope, receive=replay_receive)
            )

        return limited_handler