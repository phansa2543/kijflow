from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from app.auth.infrastructure.registration_wiring import (
    make_registration_handler,
)

from app.auth.presentation.csrf import require_trusted_origin
from app.auth.presentation.registration_limit_route import RegistrationLimitRoute
from app.auth.presentation.schemas import (
    RegistrationRequest,
    RegistrationResponse,
)

from app.auth.application.errors import (
    PasswordRejected,
    RegistrationConflict,
    ScreeningUnavailable,
)

router = APIRouter(
    prefix="/auth", 
    tags=["auth"],
    route_class=RegistrationLimitRoute
)

def registration_error(
    status_code: int,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": "REGISTRATION_FAILED",
                "message": message,
            }
        },
    )

@router.post(
    "/register",
    status_code=201,
    response_model=RegistrationResponse,
    dependencies=[Depends(require_trusted_origin)],
)
def register(
    payload: RegistrationRequest,
    request: Request,
):
    handler = make_registration_handler(
        engine=request.app.state.db_engine,
        common_passwords=request.app.state.common_passwords,
        hibp_client=request.app.state.hibp_client,
    )

    try:
        handler(payload.email, payload.password)
    except RegistrationConflict:
        return registration_error(
            409, "Registration could not be completed"
        )
    except ScreeningUnavailable:
        return registration_error(
            503, "Registration temporarily unavailable"
        )
    except (PasswordRejected, ValueError):
        return registration_error(
            422, "Invalid registration data"
        )
    except Exception:
        return registration_error(
            500, "An unexpected error occurred"
        )

    return RegistrationResponse(
        message="Registration successful"
    )