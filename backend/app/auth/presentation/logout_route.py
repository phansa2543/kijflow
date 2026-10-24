from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError

from starlette.concurrency import run_in_threadpool

from app.auth.presentation.csrf import require_trusted_origin

from app.auth.infrastructure.session_resolution import (
    revoke_session_by_raw_token,
)

logout_router = APIRouter(prefix="/auth", tags=["auth"])


def _revoke_session(engine, raw_token: object) -> bool:
    with engine.begin() as connection:
        return revoke_session_by_raw_token(
            connection,
            raw_token=raw_token,
        )


@logout_router.post(
        "/logout",
        dependencies=[Depends(require_trusted_origin)]
)
async def logout(request: Request):
    raw_token = request.cookies.get("kijflow_session")

    if raw_token is None:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"},
            headers={"Cache-Control": "no-store"},
        )

    try:
        revoked = await run_in_threadpool(
            _revoke_session,
            request.app.state.db_engine,
            raw_token,
        )
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"detail": "Logout temporarily unavailable"},
            headers={"Cache-Control": "no-store"},
        )

    if not revoked:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"},
            headers={"Cache-Control": "no-store"},
        )

    response = JSONResponse(
        status_code=200,
        content={"message": "Logout successful"},
        headers={"Cache-Control": "no-store"},
    )

    response.delete_cookie(
        key="kijflow_session",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return response