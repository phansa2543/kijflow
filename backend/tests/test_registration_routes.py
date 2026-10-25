import pytest

from functools import partial
from sqlalchemy import create_engine

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.auth.domain.validation_errors import (
    InvalidEmail,
    InvalidPasswordLength
)

from app.auth.application.errors import (
    PasswordRejected,
    RegistrationConflict,
    ScreeningUnavailable,
    RegistrationLimiterUnavailable
)
from app.auth.presentation.routes import router

TRUSTED_TEST_ORIGIN = "http://localhost:3100"

OriginalTestClient = TestClient

TestClient = partial(
    OriginalTestClient,
    headers={"Origin": TRUSTED_TEST_ORIGIN},
)

@pytest.mark.parametrize(
    "error, status_code, code, message",
    [
        (
            PasswordRejected("Rejected"),
            422,
            "PASSWORD_REJECTED",
            "Password is not allowed",
        ),
        (
            InvalidEmail("Invalid email"),
            422,
            "INVALID_EMAIL",
            "Invalid email"
        ),
        (
            InvalidPasswordLength("Invalid length"),
            422,
            "INVALID_PASSWORD_LENGTH",
            "Invalid password length"
        ),
        (
            ValueError("Unexpected validation"),
            500,
            "REGISTRATION_FAILED",
            "An unexpected error occurred"
        ),
        (
            RegistrationConflict("Duplicate email"),
            409,
            "REGISTRATION_FAILED",
            "Registration could not be completed",
        ),
        (
            ScreeningUnavailable("HIBP unavailable"),
            503,
            "REGISTRATION_FAILED",
            "Registration temporarily unavailable",
        ),
        (
            RuntimeError("Internal secret"),
            500,
            "REGISTRATION_FAILED",
            "An unexpected error occurred",
        ),
    ],
)
def test_registration_error_mapping(error, status_code, code, message):
    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
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
            "code": code,
            "message": message,
        }
    }

    assert "Internal secret" not in response.text
    assert "Duplicate email" not in response.text

    assert "Unexpected validation" not in response.text

def test_registration_success_response():
    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
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
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
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
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
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

def test_missing_email_does_not_leak_password(caplog, capsys):
    secret = "B1_SECRET_TEST_MARKER_123"

    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    handler = Mock()

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ) as limiter,
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=handler,
        ) as handler_factory,
    ):
        client = TestClient(
            app,
            client=("192.0.2.10", 12345),
        )

        response = client.post(
            "/auth/register",
            json={"password": secret},
        )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Invalid registration data",
        }
    }
    assert response.headers["cache-control"] == "no-store"

    assert secret not in response.text
    assert secret not in caplog.text

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err

    limiter.assert_called_once()
    handler_factory.assert_not_called()
    handler.assert_not_called()

def test_invalid_password_type_does_not_leak_password(
    caplog, capsys
):
    secret = "B1_SECRET_INVALID_TYPE_123"

    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    handler = Mock()

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ) as limiter,
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=handler,
        ) as handler_factory,
    ):
        client = TestClient(
            app,
            client=("192.0.2.10", 12345),
        )

        response = client.post(
            "/auth/register",
            json={
                "email": "alice@example.com",
                "password": {"secret": secret},
            },
        )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Invalid registration data",
        }
    }
    assert response.headers["cache-control"] == "no-store"

    assert secret not in response.text
    assert secret not in caplog.text

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err

    limiter.assert_called_once()
    handler_factory.assert_not_called()
    handler.assert_not_called()

def test_malformed_json_does_not_leak_password(caplog, capsys):
    secret = "B1_SECRET_MALFORMED_JSON_123"

    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    handler = Mock()

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ) as limiter,
        patch(
            "app.auth.presentation.routes.make_registration_handler",
            return_value=handler,
        ) as handler_factory,
    ):
        client = TestClient(
            app,
            client=("192.0.2.10", 12345),
        )

        malformed_body = (
            '{"email":"alice@example.com",'
            f'"password":"{secret}"'
        )

        response = client.post(
            "/auth/register",
            content=malformed_body,
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Invalid registration data",
        }
    }

    assert response.headers["cache-control"] == "no-store"
    assert secret not in response.text
    assert secret not in caplog.text

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err

    limiter.assert_called_once()
    handler_factory.assert_not_called()
    handler.assert_not_called()

@pytest.mark.parametrize(
    "origin",
    [
        None,
        "https://evil.example",
        "null",
        "http://localhost:3000",
    ],
)
def test_untrusted_origin_cannot_reach_registration_handler(origin):
    from fastapi.testclient import TestClient as RawTestClient

    test_app = FastAPI()
    test_app.state.trusted_frontend_origin = "http://localhost:3100"
    test_app.state.db_engine = Mock()
    test_app.state.registration_rate_limit_threshold = 10
    test_app.state.registration_rate_limit_window_seconds = 900
    test_app.include_router(router)

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ),
        patch(
            "app.auth.presentation.routes.make_registration_handler",
        ) as handler_factory,
    ):
        headers = {} if origin is None else {"Origin": origin}

        with RawTestClient(
            test_app,
            client=("192.0.2.40", 12345),
        ) as client:
            response = client.post(
                "/auth/register",
                json={
                    "email": "alice@example.com",
                    "password": "ExamplePassword123!",
                },
                headers=headers,
            )

    assert response.status_code == 403
    handler_factory.assert_not_called()

def test_duplicate_origin_cannot_reach_registration_handler():
    from fastapi.testclient import TestClient as RawTestClient

    test_app = FastAPI()
    test_app.state.trusted_frontend_origin = "http://localhost:3100"
    test_app.state.db_engine = Mock()
    test_app.state.registration_rate_limit_threshold = 10
    test_app.state.registration_rate_limit_window_seconds = 900
    test_app.include_router(router)

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ),
        patch(
            "app.auth.presentation.routes.make_registration_handler",
        ) as handler_factory,
    ):
        with RawTestClient(
            test_app,
            client=("192.0.2.40", 12345),
        ) as client:
            response = client.post(
                "/auth/register",
                json={
                    "email": "alice@example.com",
                    "password": "ExamplePassword123!",
                },
                headers=[
                    ("Origin", "http://localhost:3100"),
                    ("Origin", "https://evil.example"),
                ],
            )

    assert response.status_code == 403
    handler_factory.assert_not_called()

def test_registration_framework_validation_is_generic():
    app = FastAPI()
    app.state.trusted_frontend_origin = TRUSTED_TEST_ORIGIN
    app.include_router(router)

    app.state.db_engine = Mock()
    app.state.common_passwords = set()
    app.state.hibp_client = Mock()

    app.state.registration_rate_limit_threshold = 10
    app.state.registration_rate_limit_window_seconds = 900

    with (
        patch(
            "app.auth.presentation.registration_limit_route.make_registration_limit_checker",
            return_value=Mock(),
        ),
        patch(
            "app.auth.presentation.routes.make_registration_handler",
        ) as handler,
    ):
        client = TestClient(app, client=("192.0.2.10", 12345))

        response = client.post(
            "/auth/register",
            json={"email": "alice@example.com"},
        )

        handler.assert_not_called()

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "REGISTRATION_FAILED",
            "message": "Invalid registration data",
        }
    }