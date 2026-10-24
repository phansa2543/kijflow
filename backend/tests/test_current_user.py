
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import insert, update

from app.auth.presentation.current_user import (
    require_current_user_id,
)
from app.auth.infrastructure.session_token import (
    generate_session_token,
    digest_session_token,
)
from app.models.auth_session import AuthSession
from app.models.user import User


@pytest.fixture
def client(engine):
    app = FastAPI()
    app.state.db_engine = engine

    @app.get("/test/current-user")
    async def current_user(
        user_id: uuid.UUID = Depends(require_current_user_id),
    ):
        return {"user_id": str(user_id)}

    with TestClient(app) as test_client:
        yield test_client


def create_user_and_session(engine):
    user_id = uuid.uuid4()
    token = generate_session_token()

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )
        connection.execute(
            insert(AuthSession).values(
                id=uuid.uuid4(),
                user_id=user_id,
                token_digest=digest_session_token(token),
                expires_at=(
                    datetime.now(timezone.utc)
                    + timedelta(hours=1)
                ),
            )
        )

    return user_id, token


def cleanup_user(engine, user_id):
    with engine.begin() as connection:
        connection.execute(
            AuthSession.__table__.delete().where(
                AuthSession.user_id == user_id
            )
        )
        connection.execute(
            User.__table__.delete().where(
                User.id == user_id
            )
        )


def test_valid_cookie_resolves_user(client, engine):
    user_id, token = create_user_and_session(engine)

    try:
        client.cookies.set("kijflow_session", token)

        response = client.get("/test/current-user")

        assert response.status_code == 200
        assert response.json() == {"user_id": str(user_id)}
    finally:
        cleanup_user(engine, user_id)


@pytest.mark.parametrize(
    "token",
    [None, "", "short", "a" * 44, "a" * 43],
)
def test_invalid_cookie_denied(client, token):
    cookies = (
        {"kijflow_session": token}
        if token is not None
        else {}
    )

    client.cookies.set("kijflow_session", token)

    response = client.get("/test/current-user")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


@pytest.mark.parametrize("state", ["expired", "revoked"])
def test_inactive_session_denied(client, engine, state):
    user_id, token = create_user_and_session(engine)
    digest = digest_session_token(token)
    now = datetime.now(timezone.utc)

    try:
        with engine.begin() as connection:
            values = (
                {
                    "created_at": now - timedelta(hours=2),
                    "expires_at": now - timedelta(hours=1),
                }
                if state == "expired"
                else {"revoked_at": now + timedelta(seconds=1)}
            )

            connection.execute(
                update(AuthSession)
                .where(AuthSession.token_digest == digest)
                .values(**values)
            )

        client.cookies.set("kijflow_session", token)

        response = client.get("/test/current-user")

        assert response.status_code == 401
    finally:
        cleanup_user(engine, user_id)


def test_client_identity_claim_cannot_override(client, engine):
    user_id, token = create_user_and_session(engine)
    attacker_id = uuid.uuid4()

    try:
        client.cookies.clear()
        client.cookies.set("kijflow_session", token)

        response = client.get(
            "/test/current-user",
            params={"user_id": str(attacker_id)},
            headers={"X-User-ID": str(attacker_id)},
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == str(user_id)
        assert response.json()["user_id"] != str(attacker_id)
    finally:
        cleanup_user(engine, user_id)


def test_database_failure_returns_503(client):
    with patch(
        "app.auth.presentation.current_user._resolve_user_id",
        side_effect=__import__("sqlalchemy").exc.OperationalError(
            "SELECT", {}, Exception("db unavailable")
        ),
    ):
        client.cookies.clear()
        client.cookies.set(
            "kijflow_session",
            generate_session_token(),
        )

        response = client.get("/test/current-user")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Authentication temporarily unavailable"
    )
