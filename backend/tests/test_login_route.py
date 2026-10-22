import uuid

from unittest.mock import patch

from fastapi.testclient import TestClient

from sqlalchemy import text
from sqlalchemy import insert, select, delete

from app.main import app

from app.models.user import User
from app.models.password_credential import UserPasswordCredential
from app.models.auth_session import AuthSession

import app.auth.infrastructure.login_wiring as login_wiring
from app.auth.infrastructure.session_token import digest_session_token
from app.auth.infrastructure.login_counter_identifier import (
    make_account_counter_identifier
)
from app.auth.infrastructure.password_hash import hash_password
from app.auth.infrastructure.login_rate_limit import LoginLimiterUnavailable

def test_invalid_json_consumes_source_reservation(engine):
    source = f"198.51.100.{uuid.uuid4().int % 200 + 1}"

    original_engine = getattr(app.state, "db_engine", None)

    try:
        with TestClient(app, client=(source, 50000)) as client:
            # บังคับให้ Login ใช้ฐานข้อมูล Test เท่านั้น
            app.state.db_engine = engine

            try:
                response = client.post(
                    "/auth/login",
                    content="{invalid-json",
                    headers={"Content-Type": "application/json"},
                )

                assert response.status_code == 400

                with engine.connect() as connection:
                    count = connection.execute(
                        text("""
                            SELECT SUM(attempt_count)
                            FROM auth_login_attempt_counters
                            WHERE dimension = 'SOURCE'
                              AND identifier = :identifier
                        """),
                        {"identifier": source},
                    ).scalar_one()

                assert count == 1

            finally:
                app.state.db_engine = original_engine

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": source},
            )

def test_login_source_rate_limit_returns_429(engine):
    source = f"198.51.100.{uuid.uuid4().int % 200 + 1}"
    original_engine = getattr(app.state, "db_engine", None)

    try:
        with TestClient(app, client=(source, 50000)) as client:
            app.state.db_engine = engine

            responses = [
                client.post(
                    "/auth/login",
                    content="{invalid-json",
                    headers={"Content-Type": "application/json"},
                )
                for _ in range(31)
            ]

            assert all(r.status_code == 400 for r in responses[:30])
            assert responses[30].status_code == 429
            assert int(responses[30].headers["Retry-After"]) > 0
            assert responses[30].json()["error"]["code"] == "LOGIN_FAILED"

            with engine.connect() as connection:
                total = connection.execute(
                    text("""
                        SELECT SUM(attempt_count)
                        FROM auth_login_attempt_counters
                        WHERE dimension = 'SOURCE'
                          AND identifier = :identifier
                    """),
                    {"identifier": source},
                ).scalar_one()

            assert total == 31

    finally:
        app.state.db_engine = original_engine

        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": source},
            )

def test_login_account_rate_limit_returns_429(engine, monkeypatch):
    email = f"missing-{uuid.uuid4().hex}@example.com"
    source = "198.51.100.250"
    secret = bytes(range(32))

    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        secret.hex(),
    )

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state,
        "dummy_password_hash",
        hash_password("dummy-test-password"),
        raising=False,
    )

    identifier = make_account_counter_identifier(email, secret)

    try:
        client = TestClient(app, client=(source, 50000))

        try:
            assert app.state.db_engine is engine

            responses = [
                client.post(
                    "/auth/login",
                    json={
                        "email": email,
                        "password": "invalid-password",
                    },
                )
                for _ in range(11)
            ]
        finally:
            client.close()

        assert all(r.status_code == 401 for r in responses[:10])
        assert responses[10].status_code == 429
        assert int(responses[10].headers["Retry-After"]) > 0

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT SUM(attempt_count)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            ).scalar_one()

        assert count == 11

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE
                        (dimension = 'ACCOUNT' AND identifier = :account)
                        OR
                        (dimension = 'SOURCE' AND identifier = :source)
                """),
                {
                    "account": identifier,
                    "source": source,
                },
            )

def test_successful_login_commits_session_and_releases_account(
    engine, monkeypatch
):
    user_id = uuid.uuid4()
    email = f"login-success-{uuid.uuid4().hex}@example.com"
    password = "CorrectPassword2026!"
    source = "198.51.100.251"
    secret = bytes(range(32))

    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        secret.hex(),
    )
    monkeypatch.setattr(
        app.state, "db_engine", engine, raising=False
    )
    monkeypatch.setattr(
        app.state,
        "dummy_password_hash",
        hash_password("dummy-test-password"),
        raising=False,
    )

    account_identifier = make_account_counter_identifier(
        email, secret
    )

    stored_password_hash = hash_password(password)

    with engine.begin() as connection:
        connection.execute(insert(User).values(id=user_id))
        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=stored_password_hash,
            )
        )

    try:
        client = TestClient(
            app,
            client=(source, 50000),
        )

        try:
            response = client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )
        finally:
            client.close()

        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"

        cookie_header = response.headers["set-cookie"]
        assert "kijflow_session=" in cookie_header
        assert "httponly" in cookie_header.lower()
        assert "secure" in cookie_header.lower()

        token = response.cookies["kijflow_session"]

        with engine.connect() as connection:
            session = connection.execute(
                select(
                    AuthSession.user_id,
                    AuthSession.token_digest
                ).where(
                    AuthSession.user_id == user_id
                )
            ).one()

            counts = connection.execute(
                text("""
                    SELECT dimension, attempt_count
                    FROM auth_login_attempt_counters
                    WHERE
                        (dimension = 'ACCOUNT'
                         AND identifier = :account)
                        OR
                        (dimension = 'SOURCE'
                         AND identifier = :source)
                """),
                {
                    "account": account_identifier,
                    "source": source,
                },
            ).all()

        assert session.user_id == user_id
        assert session.token_digest == digest_session_token(token)

        counter_values = {
            row.dimension: row.attempt_count
            for row in counts
        }

        assert counter_values["ACCOUNT"] == 0
        assert counter_values["SOURCE"] == 1

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
                    WHERE identifier IN (:account, :source)
                """),
                {
                    "account": account_identifier,
                    "source": source,
                },
            )

def test_login_succeeds_when_account_release_fails(engine, monkeypatch):
    user_id = uuid.uuid4()
    email = f"release-failure-{uuid.uuid4().hex}@example.com"
    password = "CorrectPassword2026!"
    source = "198.51.100.252"
    secret = bytes(range(32))

    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", secret.hex())
    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state,
        "dummy_password_hash",
        hash_password("dummy-test-password"),
        raising=False,
    )

    identifier = make_account_counter_identifier(email, secret)

    with engine.begin() as connection:
        connection.execute(insert(User).values(id=user_id))
        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=hash_password(password),
            )
        )

    try:
        with patch(
            "app.auth.presentation.login_route.release_account_attempt",
            side_effect=LoginLimiterUnavailable("simulated failure"),
        ) as mocked_release:
            client = TestClient(
                app,
                client=(source, 50000),
            )

            try:
                response = client.post(
                    "/auth/login",
                    json={"email": email, "password": password},
                )
            finally:
                client.close()

        assert response.status_code == 200
        assert "kijflow_session" in response.cookies
        mocked_release.assert_called_once()

        with engine.connect() as connection:
            session_count = connection.execute(
                select(AuthSession.id).where(
                    AuthSession.user_id == user_id
                )
            ).all()

            account_count = connection.execute(
                text("""
                    SELECT SUM(attempt_count)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            ).scalar_one()

        assert len(session_count) == 1
        assert account_count == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(AuthSession).where(AuthSession.user_id == user_id)
            )
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )
            connection.execute(delete(User).where(User.id == user_id))
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE identifier IN (:account, :source)
                """),
                {"account": identifier, "source": source},
            )

def test_invalid_email_consumes_source_without_account(engine, monkeypatch):
    source = "198.51.100.253"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)

    client = TestClient(app, client=(source, 50000))

    try:

        with (
            patch(
                "app.auth.presentation.login_route.reserve_login_attempt"
            ) as account_reserve,
            patch(
                "app.auth.presentation.login_route.make_login_handler"
            ) as login_handler
        ):
            
            response = client.post(
                "/auth/login",
                json={
                    "email": "not-an-email",
                    "password": "some-password",
                },
            )

            account_reserve.assert_not_called()
            login_handler.assert_not_called()

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT dimension, identifier, SUM(attempt_count) AS total
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :source
                    GROUP BY dimension, identifier
                """),
                {"source": source},
            ).all()

        assert len(rows) == 1
        assert rows[0].total == 1

    finally:
        client.close()

        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :source
                """),
                {"source": source},
            )

def test_account_reservation_failure_stops_login(engine, monkeypatch):
    source = "198.51.100.254"
    email = f"failure-{uuid.uuid4().hex}@example.com"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        bytes(range(32)).hex(),
    )

    def fail_account_reservation(
        engine,
        *,
        dimension,
        identifier,
        window_seconds,
        limit,
    ):
        assert dimension == "ACCOUNT"
        raise LoginLimiterUnavailable("simulated database failure")

    client = TestClient(app, client=(source, 50000))

    try:
        with (
            patch(
                "app.auth.presentation.login_route.reserve_login_attempt",
                side_effect=fail_account_reservation,
            ) as mocked_reserve,
            patch(
                "app.auth.presentation.login_route.make_login_handler"
            ) as mocked_login,
            patch(
                "app.auth.presentation.login_route.make_session_creation_handler"
            ) as mocked_session,
        ):
            response = client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": "some-password",
                },
            )

            assert response.status_code == 503
            assert response.json()["error"]["code"] == "LOGIN_FAILED"
            assert "kijflow_session" not in response.cookies

            mocked_reserve.assert_called_once()
            mocked_login.assert_not_called()
            mocked_session.assert_not_called()

        with engine.connect() as connection:
            source_count = connection.execute(
                text("""
                    SELECT SUM(attempt_count)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :source
                """),
                {"source": source},
            ).scalar_one()

        assert source_count == 1

    finally:
        client.close()

        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :source
                """),
                {"source": source},
            )

def test_source_reservation_failure_stops_login(engine, monkeypatch):
    source = "198.51.100.249"

    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)

    def fail_source_reservation(
        engine,
        *,
        dimension,
        identifier,
        window_seconds,
        limit,
    ):
        assert dimension == "SOURCE"
        raise LoginLimiterUnavailable("simulated source database failure")

    with (
        patch(
            "app.auth.presentation.login_limit_route.reserve_login_attempt",
            side_effect=fail_source_reservation,
        ) as mocked_source,
        patch(
            "app.auth.presentation.login_route.reserve_login_attempt",
        ) as mocked_account,
        patch(
            "app.auth.presentation.login_route.make_login_handler",
        ) as mocked_login,
    ):
        client = TestClient(app, client=(source, 50000))

        try:
            response = client.post(
                "/auth/login",
                json={
                    "email": "someone@example.com",
                    "password": "some-password",
                },
            )
        finally:
            client.close()

        assert response.status_code == 503
        assert response.json()["error"]["code"] == "LOGIN_FAILED"
        assert "kijflow_session" not in response.cookies

        mocked_source.assert_called_once()
        mocked_account.assert_not_called()
        mocked_login.assert_not_called()

def test_login_known_and_unknown_email_have_same_failure_response(
    engine, monkeypatch
):
    user_id = uuid.uuid4()
    known_email = f"known-{uuid.uuid4().hex}@example.com"
    unknown_email = f"unknown-{uuid.uuid4().hex}@example.com"
    source = "198.51.100.248"
    password = "CorrectPassword2026!"
    secret = bytes(range(32))

    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", secret.hex())
    monkeypatch.setattr(app.state, "db_engine", engine, raising=False)
    monkeypatch.setattr(
        app.state,
        "dummy_password_hash",
        hash_password("dummy-test-password"),
        raising=False,
    )

    stored_password_hash = hash_password(password)

    with engine.begin() as connection:
        connection.execute(insert(User).values(id=user_id))
        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=known_email,
                password_hash=stored_password_hash,
            )
        )

    try:
        client = TestClient(app, client=(source, 50000))

        try:
            verified_hashes = []
            
            original_verify = login_wiring.verify_and_prepare_rehash
    
            def tracked_verify(password, password_hash):
                verified_hashes.append(password_hash)
                return original_verify(password, password_hash)

            with patch.object(
                login_wiring,
                "verify_and_prepare_rehash",
                side_effect=tracked_verify
            ):
                known_response = client.post(
                    "/auth/login",
                    json={
                        "email": known_email,
                        "password": "wrong-password",
                    },
                )
                unknown_response = client.post(
                    "/auth/login",
                    json={
                        "email": unknown_email,
                        "password": "wrong-password",
                    },
                )

            assert len(verified_hashes) == 2
            assert verified_hashes[0] == stored_password_hash
            assert verified_hashes[1] == app.state.dummy_password_hash
                
        finally:
            client.close()

        assert known_response.status_code == unknown_response.status_code == 401
        assert known_response.json() == unknown_response.json()
        assert "kijflow_session" not in known_response.cookies
        assert "kijflow_session" not in unknown_response.cookies

        with engine.connect() as connection:
            session_count = connection.execute(
                select(AuthSession.id).where(
                    AuthSession.user_id == user_id
                )
            ).all()

        assert session_count == []

        known_identifier = make_account_counter_identifier(
            known_email, secret
        )
        unknown_identifier = make_account_counter_identifier(
            unknown_email, secret
        )

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT identifier, SUM(attempt_count) AS total
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier IN (:known, :unknown)
                    GROUP BY identifier
                """),
                {
                    "known": known_identifier,
                    "unknown": unknown_identifier,
                },
            ).all()

        counts = {row.identifier: row.total for row in rows}

        assert counts[known_identifier] == 1
        assert counts[unknown_identifier] == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(AuthSession).where(AuthSession.user_id == user_id)
            )
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )
            connection.execute(delete(User).where(User.id == user_id))
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :source
                       OR dimension = 'ACCOUNT'
                      AND identifier IN (:known, :unknown)
                """),
                {
                    "source": source,
                    "known": make_account_counter_identifier(
                        known_email, secret
                    ),
                    "unknown": make_account_counter_identifier(
                        unknown_email, secret
                    ),
                },
            )