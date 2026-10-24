
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert, delete, select, text

from app.main import app
from app.models.user import User
from app.models.password_credential import UserPasswordCredential
from app.models.auth_session import AuthSession
from app.auth.infrastructure.password_hash import hash_password
from app.auth.infrastructure.login_counter_identifier import (
    make_account_counter_identifier,
)

@pytest.fixture(autouse=True)
def trusted_origin_for_session_lifetime(monkeypatch):
    monkeypatch.setenv(
        "TRUSTED_FRONTEND_ORIGIN",
        "http://localhost:3100",
    )

@pytest.mark.parametrize(
    "configured_lifetime, expected_seconds",
    [
        (None, 86400),  # Default: 24 hours
        ("3600", 3600),  # Custom: 1 hour
    ],
)
def test_session_and_cookie_share_lifetime(
    engine,
    monkeypatch,
    configured_lifetime,
    expected_seconds,
):
    user_id = uuid.uuid4()
    email = f"session-lifetime-{uuid.uuid4().hex}@example.com"
    password = "CorrectPassword2026!"

    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        "a1" * 32,
    )

    monkeypatch.delenv(
        "SESSION_LIFETIME_SECONDS",
        raising=False,
    )

    if configured_lifetime is not None:
        monkeypatch.setenv(
            "SESSION_LIFETIME_SECONDS",
            configured_lifetime,
        )

    monkeypatch.setenv("LOGIN_SOURCE_LIMIT", "100")
    monkeypatch.setenv("LOGIN_ACCOUNT_LIMIT", "100")

    monkeypatch.setenv(
        "TRUSTED_FRONTEND_ORIGIN",
        "http://localhost:3100"
    )

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )
        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=hash_password(password),
            )
        )

    try:
        with (
            patch("app.main.load_dotenv"),
            patch(
                "app.main.create_database_engine",
                return_value=engine,
            ),
        ):
            with TestClient(
                app,
                client=("198.51.100.245", 50000),
                headers={"Origin": "http://localhost:3100"}
            ) as client:
                response = client.post(
                    "/auth/login",
                    json={
                        "email": email,
                        "password": password,
                    },
                )

        assert response.status_code == 200

        cookie_header = response.headers["set-cookie"]
        assert f"Max-Age={expected_seconds}" in cookie_header
        assert "kijflow_session" in response.cookies

        with engine.connect() as connection:
            session = connection.execute(
                select(
                    AuthSession.created_at,
                    AuthSession.expires_at    
                ).where(
                    AuthSession.user_id == user_id
                )
            ).one()

        actual_seconds = (
            session.expires_at - session.created_at
        ).total_seconds()

        assert abs(actual_seconds - expected_seconds) < 10

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(AuthSession).where(
                    AuthSession.user_id == user_id
                )
            )
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )
            connection.execute(
                delete(User).where(User.id == user_id)
            )

            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {
                    "identifier": make_account_counter_identifier(
                        email,
                        bytes.fromhex("a1" * 32),
                    )
                },
            )


@pytest.mark.parametrize(
    "invalid_value",
    ["0", "-1", "abc", ""],
)
def test_invalid_session_lifetime_fails_before_engine(
    monkeypatch,
    invalid_value,
):
    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        "a1" * 32,
    )
    monkeypatch.setenv(
        "SESSION_LIFETIME_SECONDS",
        invalid_value,
    )

    with (
        patch("app.main.load_dotenv"),
        patch("app.main.create_database_engine") as create_engine,
    ):
        with pytest.raises(
            ValueError,
            match="Invalid configuration: SESSION_LIFETIME_SECONDS",
        ):
            with TestClient(app):
                pass

        create_engine.assert_not_called()
