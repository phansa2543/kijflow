
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import insert, select, update
from sqlalchemy.exc import OperationalError

from app.auth.presentation.logout_route import logout_router
from app.models.user import User
from app.models.auth_session import AuthSession
from app.auth.infrastructure.session_token import (
    generate_session_token,
    digest_session_token,
)
from app.auth.infrastructure.session_resolution import (
    resolve_session_user_id,
)


@pytest.fixture
def client(engine):
    test_app = FastAPI()
    test_app.state.trusted_frontend_origin = "http://localhost:3100"
    test_app.state.db_engine = engine
    test_app.include_router(logout_router)

    with TestClient(
        test_app,
        base_url="https://testserver",
        headers={"Origin": "http://localhost:3100"},
    ) as test_client:
        yield test_client


@pytest.fixture
def session_data(engine):
    user_id = uuid.uuid4()
    first_token = generate_session_token()
    second_token = generate_session_token()

    now = datetime.now(timezone.utc)

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        for token in (first_token, second_token):
            connection.execute(
                insert(AuthSession).values(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    token_digest=digest_session_token(token),
                    expires_at=now + timedelta(hours=1),
                )
            )

    try:
        yield user_id, first_token, second_token
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


def test_logout_revokes_current_session(
    client,
    engine,
    session_data,
):
    user_id, first_token, second_token = session_data

    client.cookies.clear()

    response = client.post(
        "/auth/logout",
        headers={
            "Cookie": f"kijflow_session={first_token}",
        },
    )

    assert "kijflow_session" in response.request.headers.get("cookie", "")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert "kijflow_session" not in client.cookies

    with engine.connect() as connection:
        assert resolve_session_user_id(
            connection,
            raw_token=first_token,
        ) is None

        assert resolve_session_user_id(
            connection,
            raw_token=second_token,
        ) == user_id


def test_logout_rejects_missing_cookie(client):
    client.cookies.clear()

    response = client.post("/auth/logout")

    assert response.status_code == 401


@pytest.mark.parametrize(
    "token",
    ["", "short", "a" * 44, generate_session_token()],
)
def test_logout_rejects_invalid_or_unknown_token(client, token):
    client.cookies.clear()
    client.cookies.set("kijflow_session", token)

    response = client.post("/auth/logout")

    assert response.status_code == 401


@pytest.mark.parametrize("state", ["expired", "revoked"])
def test_logout_rejects_inactive_session(
    client,
    engine,
    session_data,
    state,
):
    _, first_token, _ = session_data
    digest = digest_session_token(first_token)
    now = datetime.now(timezone.utc)

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

    client.cookies.set("kijflow_session", first_token)

    response = client.post("/auth/logout")

    assert response.status_code == 401


def test_logout_database_failure_is_not_success(
    client,
    session_data,
):
    _, first_token, _ = session_data
    client.cookies.set("kijflow_session", first_token)

    with patch(
        "app.auth.presentation.logout_route._revoke_session",
        side_effect=OperationalError(
            "UPDATE", {}, Exception("database unavailable")
        ),
    ):
        response = client.post("/auth/logout")

    assert response.status_code == 503
    assert "Logout successful" not in response.text
    assert "Set-Cookie" not in response.headers


def test_logout_cannot_select_session_via_query_or_header(
    client,
    engine,
    session_data,
):
    user_id, first_token, second_token = session_data

    client.cookies.clear()
    client.cookies.set(
        "kijflow_session",
        first_token,
        path="/",
    )

    response = client.post(
        "/auth/logout",
        params={"session_token": second_token},
        headers={
            "Cookie": f"kijflow_session={first_token}",
            "X-Session-Token": second_token,
        },
    )

    assert response.status_code == 200

    with engine.connect() as connection:
        assert resolve_session_user_id(
            connection,
            raw_token=first_token,
        ) is None

        assert resolve_session_user_id(
            connection,
            raw_token=second_token,
        ) == user_id

@pytest.mark.parametrize(
    "origin",
    [
        None,
        "https://evil.example",
        "null",
        "http://localhost:3000",
    ],
)
def test_untrusted_origin_cannot_revoke_session(
    client,
    engine,
    session_data,
    origin,
):
    user_id, first_token, _ = session_data

    headers = {
        "Cookie": f"kijflow_session={first_token}",
    }

    if origin is not None:
        headers["Origin"] = origin

    # Explicitly override the trusted default for each request.
    client.headers.pop("Origin", None)

    response = client.post(
        "/auth/logout",
        headers=headers,
    )

    assert response.status_code == 403
    assert "Set-Cookie" not in response.headers

    with engine.connect() as connection:
        assert resolve_session_user_id(
            connection,
            raw_token=first_token,
        ) == user_id

def test_duplicate_origin_cannot_revoke_session(
    client,
    engine,
    session_data,
):
    user_id, first_token, _ = session_data

    response = client.post(
        "/auth/logout",
        headers=[
            ("Origin", "http://localhost:3100"),
            ("Origin", "https://evil.example"),
            ("Cookie", f"kijflow_session={first_token}"),
        ],
    )

    assert response.status_code == 403
    assert "set-cookie" not in response.headers

    with engine.connect() as connection:
        assert resolve_session_user_id(
            connection,
            raw_token=first_token,
        ) == user_id