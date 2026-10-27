import uuid, pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import insert, update
from sqlalchemy.exc import OperationalError

from app.auth.presentation.session_route import session_router
from app.auth.infrastructure.session_token import (
    generate_session_token,
    digest_session_token,
)
from app.models.user import User
from app.models.auth_session import AuthSession


@pytest.fixture
def client(engine):
    test_app = FastAPI()
    test_app.state.db_engine = engine
    test_app.include_router(session_router)

    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def session_data(engine):
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

    try:
        yield user_id, token
    finally:
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

def test_valid_session_returns_204(
    client,
    session_data,
):
    _, token = session_data

    client.cookies.set("kijflow_session", token)

    response = client.get("/auth/session")

    assert response.status_code == 204
    assert response.content == b""
    assert response.headers["Cache-Control"] == "no-store"
    assert "Set-Cookie" not in response.headers

@pytest.mark.parametrize(
    "token",
    [None, "", "short", "a" * 44, generate_session_token()],
)
def test_invalid_session_returns_401(client, token):
    client.cookies.clear()

    if token is not None:
        client.cookies.set("kijflow_session", token)

    response = client.get("/auth/session")

    assert response.status_code == 401
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["detail"] == "Authentication required"
    assert "Set-Cookie" not in response.headers

@pytest.mark.parametrize("state", ["expired", "revoked"])
def test_inactive_session_returns_401(
    client,
    engine,
    session_data,
    state,
):
    _, token = session_data
    digest = digest_session_token(token)
    now = datetime.now(timezone.utc)

    with engine.begin() as connection:
        values = (
            {
                "created_at": now - timedelta(hours=2),
                "expires_at": now - timedelta(hours=1),
            }
            if state == "expired"
            else {"revoked_at": now}
        )

        connection.execute(
            update(AuthSession)
            .where(AuthSession.token_digest == digest)
            .values(**values)
        )

    client.cookies.set("kijflow_session", token)

    response = client.get("/auth/session")

    assert response.status_code == 401
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["detail"] == "Authentication required"
    assert "Set-Cookie" not in response.headers

def test_session_database_failure_returns_503(
    client,
    session_data,
):
    _, token = session_data
    client.cookies.set("kijflow_session", token)

    with patch(
        "app.auth.presentation.current_user._resolve_user_id",
        side_effect=OperationalError(
            "SELECT",
            {},
            Exception("database unavailable"),
        ),
    ):
        response = client.get("/auth/session")

    assert response.status_code == 503
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["detail"] == (
        "Authentication temporarily unavailable"
    )
    assert "Set-Cookie" not in response.headers