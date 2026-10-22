import logging

from datetime import timedelta

from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError

from starlette.concurrency import run_in_threadpool

from app.auth.domain.email import canonicalize_email
from app.auth.infrastructure.login_counter_identifier import (
    load_login_counter_hmac_secret,
    make_account_counter_identifier,
)
from app.auth.infrastructure.login_rate_limit import (
    reserve_login_attempt,
    release_account_attempt,
    LoginLimiterUnavailable,
)
from app.auth.infrastructure.login_wiring import make_login_handler
from app.auth.infrastructure.session_wiring import (
    make_session_creation_handler,
)
from app.auth.presentation.login_limit_route import LoginLimitRoute
from app.auth.presentation.schemas import LoginRequest, LoginResponse

login_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    route_class=LoginLimitRoute,
)

logger = logging.getLogger(__name__)

def login_error(
    status_code: int,
    message: str,
    retry_after_seconds: int | None = None,
) -> JSONResponse:
    headers = {"Cache-Control": "no-store"}

    if retry_after_seconds is not None:
        headers["Retry-After"] = str(retry_after_seconds)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": "LOGIN_FAILED",
                "message": message,
            }
        },
        headers=headers,
    )

@login_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request):
    engine = request.app.state.db_engine

    try:
        canonical_email = canonicalize_email(payload.email)
    except ValueError:
        return login_error(401, "Invalid email or password")

    try:
        secret = load_login_counter_hmac_secret()

        identifier = make_account_counter_identifier(
            canonical_email,
            secret,
        )

        reservation = await run_in_threadpool(
            reserve_login_attempt,
            engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=request.app.state.login_account_window_seconds,
            limit=request.app.state.login_account_limit,
        )

    except (LoginLimiterUnavailable, ValueError):
        return login_error(503, "Login temporarily unavailable")

    if not reservation.allowed:
        return login_error(
            429,
            "Too many requests",
            reservation.retry_after_seconds,
        )

    login_handler = make_login_handler(
        engine=engine,
        dummy_password_hash=request.app.state.dummy_password_hash,
    )

    try:
        credential = await run_in_threadpool(
            login_handler,
            canonical_email,
            payload.password,
        )
    except ValueError:
        return login_error(401, "Invalid email or password")
    except SQLAlchemyError:
        return login_error(503, "Login temporarily unavailable")

    if credential is None:
        return login_error(401, "Invalid email or password")
    
    user_id, expected_hash = credential

    session_handler = make_session_creation_handler(
        engine=engine,
        session_lifetime=timedelta(days=7),
    )

    try:
        token = await run_in_threadpool(
            session_handler,
            user_id,
            expected_hash,
        )
    except SQLAlchemyError:
        return login_error(503, "Login temporarily unavailable")

    if token is None:
        return login_error(401, "Invalid email or password")

    try:
        await run_in_threadpool(
            release_account_attempt,
            engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds,
        )
    except LoginLimiterUnavailable:
        logger.warning("Login ACCOUNT counter release failed")

    response = JSONResponse(
        status_code=200,
        content={"message": "Login successful"},
        headers={"Cache-Control": "no-store"},
    )

    response.set_cookie(
        key="kijflow_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
    )

    return response