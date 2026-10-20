import pytest

from sqlalchemy import create_engine

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.auth.application.errors import (
    PasswordRejected,
    RegistrationConflict,
    ScreeningUnavailable,
    RegistrationLimiterUnavailable
)
from app.auth.presentation.routes import router


@pytest.mark.parametrize(
    "error, status_code, message",
    [
        (
            PasswordRejected("Rejected"),
            422,
            "Invalid registration data",
        ),
        (
            ValueError("Invalid email"),
            422,
            "Invalid registration data",
        ),
        (
            RegistrationConflict("Duplicate email"),
            409,
            "Registration could not be completed",
        ),
        (
            ScreeningUnavailable("HIBP unavailable"),
            503,
            "Registration temporarily unavailable",
        ),
        (
            RuntimeError("Internal secret"),
            500,
            "An unexpected error occurred",
        ),
    ],
)
def test_registration_error_mapping(error, status_code, message):
    app = FastAPI()
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.common_passwords = set()
    app.state.hibp_client = Mock()

    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock()
        ) as mocked_limiter,
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=Mock(side_effect=error),
        )
    ):
        client = TestClient(app, client=("192.0.2.10", 12345))

        response = client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "password": "ExamplePassword123!",
            },
        )

        mocked_limiter.assert_called_once()

    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": message,
        }
    }

    assert "Internal secret" not in response.text
    assert "Duplicate email" not in response.text

def test_registration_success_response():
    app = FastAPI()
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.common_passwords = set()
    app.state.hibp_client = Mock()

    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    mocked_handler = Mock()

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock()
        ) as mocked_limiter,
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=mocked_handler,
        )
    ):
        client = TestClient(app, client=("192.0.2.10", 12345))

        response = client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "password": "ExamplePassword123!",
            },
        )

        mocked_limiter.assert_called_once()

    assert response.status_code == 201
    assert response.json() == {
        "message": "Registration successful"
    }

    mocked_handler.assert_called_once_with(
        "alice@example.com",
        "ExamplePassword123!",
    )

    assert "set-cookie" not in response.headers

def test_registration_limiter_unavailable_fails_closed():
    app = FastAPI()
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    failing_checker = Mock(
        side_effect=RegistrationLimiterUnavailable(
            "Simulated limiter failure"
        )
    )
    registration_handler = Mock()

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=failing_checker,
        ),
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=registration_handler,
        ),
    ):
        client = TestClient(
            app,
            client=("192.0.2.20", 12345),
        )

        response = client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "password": "ExamplePassword123!",
            },
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Registration temporarily unavailable",
        }
    }
    assert response.headers["cache-control"] == "no-store"

    failing_checker.assert_called_once()
    registration_handler.assert_not_called()

def test_registration_database_unavailable_fails_closed():
    app = FastAPI()
    app.include_router(router)

    unavailable_engine = create_engine(
        "postgresql+psycopg://test:test@127.0.0.1:1/test",
        connect_args={"connect_timeout": 1},
    )

    app.state.db_engine = unavailable_engine
    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    registration_handler = Mock()

    try:
        with patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=registration_handler,
        ):
            client = TestClient(
                app,
                client=("192.0.2.30", 12345),
            )

            response = client.post(
                "/auth/register",
                json={
                    "email": "alice@example.com",
                    "password": "ExamplePassword123!",
                },
            )

        assert response.status_code == 503

        assert response.json() == {
            "error": {
                "code": "REGISTRATION_FAILED",
                "message": "Registration temporarily unavailable",
            }
        }

        assert response.headers["cache-control"] == "no-store"

        registration_handler.assert_not_called()

    finally:
        unavailable_engine.dispose()