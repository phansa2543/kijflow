import uuid, httpx, pytest

from functools import partial
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from sqlalchemy import delete, select, text, func

from app.main import app
from app.models.user import User
from app.models.password_credential import UserPasswordCredential

TRUSTED_TEST_ORIGIN = "http://localhost:3100"


@pytest.fixture(autouse=True)
def trusted_registration_origin(monkeypatch):
    monkeypatch.setattr(
        app.state,
        "trusted_frontend_origin",
        TRUSTED_TEST_ORIGIN,
        raising=False,
    )

TestClient = partial(
    TestClient,
    headers={"Origin": TRUSTED_TEST_ORIGIN},
)

def test_http_registration_persists_user_and_credential(engine, monkeypatch):

    assert engine.url.database == "kijflow_test"

    email = f"http-{uuid.uuid4().hex}@example.com"
    password = "ExamplePassword123!"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(app.state, "common_passwords", set(), raising=False)
    monkeypatch.setattr(app.state, "hibp_client", Mock(), raising=False)
    monkeypatch.setattr(app.state, "registration_rate_limit_threshold", 10, raising=False)
    monkeypatch.setattr(app.state, "registration_rate_limit_window_seconds", 900, raising=False)

    client = TestClient(app, client=(client_ip, 12345))

    counts_query = text("""
        SELECT
            (SELECT COUNT(*) FROM organizations) AS organizations,
            (SELECT COUNT(*) FROM memberships) AS memberships,
            (SELECT COUNT(*) FROM auth_sessions) AS auth_sessions
    """)

    with engine.connect() as connection:
        counts_before = connection.execute(counts_query).one()

    try:

        with patch(
            "app.auth.infrastructure.hibp.is_password_compromised",
            return_value=False,
        ):
            response = client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )

        assert response.status_code == 201, response.text
        assert response.json() == {
            "message": "Registration successful"
        }
        assert "set-cookie" not in response.headers

        with engine.connect() as connection:
            credential = connection.execute(
                select(
                    UserPasswordCredential.user_id,
                    UserPasswordCredential.password_hash,
                ).where(
                    UserPasswordCredential.email == email
                )
            ).one()

            assert credential.password_hash.startswith("$argon2id$")

            user_id = connection.execute(
                select(User.id).where(
                    User.id == credential.user_id
                )
            ).scalar_one()

            assert user_id == credential.user_id

        with engine.connect() as connection:
            counts_after = connection.execute(counts_query).one()

        assert counts_after == counts_before

    finally:

        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip}
            )

            user_id = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalar_one_or_none()

            if user_id is not None:
                connection.execute(
                    delete(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    )
                )
                connection.execute(
                    delete(User).where(User.id == user_id)
                )

def test_http_registration_duplicate_email_returns_409(engine, monkeypatch):
    assert engine.url.database == "kijflow_test"

    email = f"duplicate-{uuid.uuid4().hex}@example.com"
    password = "ExamplePassword123!"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(app.state, "common_passwords", set(), raising=False)
    monkeypatch.setattr(app.state, "hibp_client", Mock(), raising=False)
    monkeypatch.setattr(app.state, "registration_rate_limit_threshold", 10, raising=False)
    monkeypatch.setattr(app.state, "registration_rate_limit_window_seconds", 900, raising=False)

    client = TestClient(app, client=(client_ip, 12345))

    try:
        with patch(
            "app.auth.infrastructure.hibp.is_password_compromised",
            return_value=False,
        ):
            first_response = client.post(
                "/auth/register",
                json={"email": email, "password": password},
            )

            assert first_response.status_code == 201

            with engine.connect() as connection:
                users_before = connection.execute(
                    select(func.count()).select_from(User)
                ).scalar_one()

                credentials_before = connection.execute(
                    select(func.count()).select_from(
                        UserPasswordCredential
                    )
                ).scalar_one()

            duplicate_response = client.post(
                "/auth/register",
                json={
                    "email": f" {email.upper()} ",
                    "password": password,
                },
            )

        assert duplicate_response.status_code == 409
        assert duplicate_response.json() == {
            "error": {
                "code": "REGISTRATION_FAILED",
                "message": "Registration could not be completed",
            }
        }

        assert "set-cookie" not in duplicate_response.headers

        with engine.connect() as connection:
            users_after = connection.execute(
                select(func.count()).select_from(User)
            ).scalar_one()

            credentials_after = connection.execute(
                select(func.count()).select_from(
                    UserPasswordCredential
                )
            ).scalar_one()

            matching_credentials = connection.execute(
                select(func.count())
                .select_from(UserPasswordCredential)
                .where(UserPasswordCredential.email == email)
            ).scalar_one()

        assert users_after == users_before
        assert credentials_after == credentials_before
        assert matching_credentials == 1

    finally:
        with engine.begin() as connection:
            user_id = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalar_one_or_none()

            if user_id is not None:
                connection.execute(
                    delete(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    )
                )
                connection.execute(
                    delete(User).where(User.id == user_id)
                )

def test_http_registration_hibp_unavailable_returns_503(
    engine, monkeypatch
):
    assert engine.url.database == "kijflow_test"

    email = f"hibp-failure-{uuid.uuid4().hex}@example.com"
    password = "ExamplePassword123!"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    hibp_client = Mock()
    hibp_client.get.side_effect = httpx.ReadTimeout(
        "Simulated HIBP timeout"
    )

    monkeypatch.setattr(
        app.state, "db_engine", engine, raising=False
    )
    monkeypatch.setattr(
        app.state, "common_passwords", set(), raising=False
    )
    monkeypatch.setattr(
        app.state, "hibp_client", hibp_client, raising=False
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_threshold", 10, raising=False
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_window_seconds", 900, raising=False
    )

    client = TestClient(app, client=(client_ip, 12345))

    with engine.connect() as connection:

        users_before = connection.execute(
            select(func.count()).select_from(User)
        ).scalar_one()

        credentials_before = connection.execute(
            select(func.count()).select_from(UserPasswordCredential)
        ).scalar_one()

    try:
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 503
        assert response.json() == {
            "error": {
                "code": "REGISTRATION_FAILED",
                "message": "Registration temporarily unavailable",
            }
        }

        assert "set-cookie" not in response.headers
        assert "Simulated HIBP timeout" not in response.text

        hibp_client.get.assert_called_once()

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                    AND window_seconds = 900
                """),
                {"client_ip": client_ip},
            ).scalar_one()

        assert count == 1

        with engine.connect() as connection:
            users_after = connection.execute(
                select(func.count()).select_from(User)
            ).scalar_one()

            credentials_after = connection.execute(
                select(func.count()).select_from(UserPasswordCredential)
            ).scalar_one()

        assert users_after == users_before
        assert credentials_after == credentials_before

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip}
            )

            user_id = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalar_one_or_none()

            if user_id is not None:
                connection.execute(
                    delete(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    )
                )
                connection.execute(
                    delete(User).where(User.id == user_id)
                )

def test_malformed_json_consumes_registration_quota(engine, monkeypatch):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    monkeypatch.setattr(
        app.state, "db_engine", engine, raising=False
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_threshold", 10,
        raising=False,
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_window_seconds", 900,
        raising=False,
    )

    client = TestClient(app, client=(client_ip, 12345))

    try:
        responses = [
            client.post(
                "/auth/register", 
                content=b"{",
                headers={"content-type": "application/json"}
            )
            for _ in range(11)
        ]

        assert [r.status_code for r in responses] == (
            [422] * 10 + [429]
        )

        blocked = responses[-1]

        assert blocked.json() == {
            "error": {
                "code": "REGISTRATION_FAILED",
                "message": "Too many requests",
            }
        }

        assert blocked.headers["cache-control"] == "no-store"
        assert 1 <= int(blocked.headers["retry-after"]) <= 900

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = 900
                """),
                {"client_ip": client_ip},
            ).scalar_one()

        assert count == 11

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_oversized_registration_body_consumes_quota(engine, monkeypatch):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state, "registration_rate_limit_threshold", 10,
        raising=False,
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_window_seconds", 900,
        raising=False,
    )

    client = TestClient(app, client=(client_ip, 12345))

    try:
        response = client.post(
            "/auth/register",
            content=b"x" * 8193,
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 413

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = 900
                """),
                {"client_ip": client_ip},
            ).scalar_one()

        assert count == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_csrf_rejected_registration_consumes_source_quota(
    engine, monkeypatch
):
    from ipaddress import ip_address

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = str(ip_address(f"2001:db8:{groups}"))

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state, "registration_rate_limit_threshold", 10,
        raising=False,
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_window_seconds", 900,
        raising=False,
    )

    try:
        client = TestClient(
            app,
            client=(client_ip, 12345),
        )

        try:
            response = client.post(
                "/auth/register",
                json={
                    "email": "csrf-registration@example.com",
                    "password": "ExamplePassword123!",
                },
                headers={"Origin": "https://evil.example"},
            )
        finally:
            client.close()

        assert response.status_code == 403
        assert "set-cookie" not in response.headers

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT COALESCE(SUM(attempt_count), 0)
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = 900
                """),
                {"client_ip": client_ip},
            ).scalar_one()

        assert count == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_csrf_rejected_registration_does_not_create_user_or_credential(
    engine, monkeypatch
):
    from ipaddress import ip_address

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = str(ip_address(f"2001:db8:{groups}"))
    email = f"csrf-rejected-{uuid.uuid4().hex}@example.com"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state, "registration_rate_limit_threshold", 10,
        raising=False,
    )
    monkeypatch.setattr(
        app.state, "registration_rate_limit_window_seconds", 900,
        raising=False,
    )

    with engine.connect() as connection:
        users_before = connection.execute(
            select(func.count()).select_from(User)
        ).scalar_one()
        credentials_before = connection.execute(
            select(func.count()).select_from(UserPasswordCredential)
        ).scalar_one()

    try:
        client = TestClient(app, client=(client_ip, 12345))

        try:
            response = client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": "ExamplePassword123!",
                },
                headers={"Origin": "https://evil.example"},
            )
        finally:
            client.close()

        assert response.status_code == 403
        assert "set-cookie" not in response.headers

        with engine.connect() as connection:
            users_after = connection.execute(
                select(func.count()).select_from(User)
            ).scalar_one()
            credentials_after = connection.execute(
                select(func.count()).select_from(UserPasswordCredential)
            ).scalar_one()

            matching_credential = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalar_one_or_none()

        assert users_after == users_before
        assert credentials_after == credentials_before
        assert matching_credential is None

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )