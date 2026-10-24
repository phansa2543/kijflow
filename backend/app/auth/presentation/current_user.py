from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from app.auth.infrastructure.session_resolution import (
    resolve_session_user_id,
)


def _resolve_user_id(engine, raw_token: object) -> UUID | None:
    with engine.connect() as connection:
        return resolve_session_user_id(
            connection,
            raw_token=raw_token,
        )


async def require_current_user_id(request: Request) -> UUID:
    raw_token = request.cookies.get("kijflow_session")

    if raw_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        user_id = await run_in_threadpool(
            _resolve_user_id,
            request.app.state.db_engine,
            raw_token,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication temporarily unavailable",
        ) from None

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user_id