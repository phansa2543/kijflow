from fastapi import (
    APIRouter, 
    Depends, 
    Response,
    HTTPException,
    Request
)

from app.auth.presentation.current_user import require_current_user_id

session_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

async def require_session_check_user_id(request: Request):
    try:
        return await require_current_user_id(request)
    except HTTPException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.detail,
            headers={
                **(exc.headers or {}),
                "Cache-Control": "no-store"
            }
        ) from None

@session_router.get("/session")
async def check_session(user_id=Depends(require_session_check_user_id)):
    return Response(
        status_code=204,
        headers={"Cache-Control": "no-store"}
    )