from app.auth.presentation.schemas import (
    RegistrationRequest,
    RegistrationResponse,
    RegistrationErrorResponse,
)


def test_registration_request_contract():
    request = RegistrationRequest(
        email="alice@example.com",
        password="ExamplePassword123!",
    )

    assert request.model_dump() == {
        "email": "alice@example.com",
        "password": "ExamplePassword123!",
    }


def test_registration_success_response_contract():
    response = RegistrationResponse(
        message="Registration successful"
    )

    assert response.model_dump() == {
        "message": "Registration successful"
    }


def test_registration_error_response_contract():
    response = RegistrationErrorResponse(
        error={
            "code": "REGISTRATION_FAILED",
            "message": "Registration could not be completed",
        }
    )

    assert response.model_dump() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Registration could not be completed",
        }
    }