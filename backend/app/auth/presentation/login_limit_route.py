from collections.abc import Callable

from fastapi import Request
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from starlette.responses import Response
from starlette.concurrency import run_in_threadpool

from app.auth.application.errors import RegistrationLimiterUnavailable

from app.auth.presentation.client_ip import resolve_direct_client_ip

from app.auth.infrastructure.login_rate_limit import (
    reserve_login_attempt,
    LoginLimiterUnavailable,
)

MAX_LOGIN_BODY_BYTES = 8_192

class LoginLimitRoute(APIRoute):
    def get_route_handler(
        self,
    ) -> Callable[[Request], Response]:

        original_handler = super().get_route_handler()

        async def limited_handler(request: Request) -> Response:
            try:
                client_ip = resolve_direct_client_ip(request)
                engine = getattr(request.app.state, "db_engine", None)

                if engine is None or not client_ip:
                    raise LoginLimiterUnavailable(
                        "login source protection unavailable"
                    )

                reservation = await run_in_threadpool(
                    reserve_login_attempt,
                    engine,
                    dimension="SOURCE",
                    identifier=client_ip,
                    window_seconds=60,
                    limit=30
                )

                if not reservation.allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": {
                                "code": "LOGIN_FAILED",
                                "message": "Too many requests"
                            }
                        },
                        headers={
                            "Retry-After": str(reservation.retry_after_seconds),
                            "Cache-Control": "no-store"
                        }
                    )
            except (
                LoginLimiterUnavailable,
                RegistrationLimiterUnavailable,
                ValueError,
            ):
                return JSONResponse(
                    status_code=503,
                    content={
                        "error": {
                            "code": "LOGIN_FAILED",
                            "message": "Login temporarily unavailable"
                        }
                    },
                    headers={"Cache-Control": "no-store"}
                )

            body = bytearray()

            async for chunk in request.stream():
                if len(chunk) > MAX_LOGIN_BODY_BYTES - len(body):
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": {
                                "code": "LOGIN_FAILED",
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

            try:
                return await original_handler(
                    Request(request.scope, receive=replay_receive)
                )
            except RequestValidationError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": {
                            "code": "LOGIN_FAILED",
                            "message": "Invalid login request",
                        }
                    },
                    headers={"Cache-Control": "no-store"},
                )

        return limited_handler