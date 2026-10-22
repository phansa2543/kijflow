import uuid, pytest

from sqlalchemy import text, insert, create_engine, event
from sqlalchemy.exc import OperationalError

from app.auth.infrastructure.login_counter_cleanup import (
    cleanup_expired_login_counters,
    LoginCounterCleanupUnavailable
)


def test_cleanup_deletes_expired_login_counter(engine):
    identifier = f"test-cleanup-{uuid.uuid4().hex}"

    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO auth_login_attempt_counters (
                        dimension,
                        identifier,
                        window_started_at,
                        window_seconds,
                        attempt_count
                    )
                    VALUES (
                        'SOURCE',
                        :identifier,
                        statement_timestamp() - INTERVAL '3 days',
                        60,
                        1
                    )
                """),
                {"identifier": identifier},
            )

        deleted = cleanup_expired_login_counters(engine=engine)

        assert deleted >= 1

        with engine.connect() as connection:
            remaining = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            ).scalar_one()

        assert remaining == 0

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            )

def test_cleanup_preserves_counter_within_retention(engine):
    identifier = f"test-retention-{uuid.uuid4().hex}"

    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO auth_login_attempt_counters (
                        dimension,
                        identifier,
                        window_started_at,
                        window_seconds,
                        attempt_count
                    )
                    VALUES (
                        'SOURCE',
                        :identifier,
                        statement_timestamp() - INTERVAL '23 hours',
                        60,
                        1
                    )
                """),
                {"identifier": identifier},
            )

        cleanup_expired_login_counters(engine=engine)

        with engine.connect() as connection:
            remaining = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            ).scalar_one()

        assert remaining == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            )

def test_cleanup_respects_batch_and_max_batches(engine):
    prefix = f"test-batch-{uuid.uuid4().hex}-"

    try:
        with engine.begin() as connection:
            for i in range(5):
                connection.execute(
                    text("""
                        INSERT INTO auth_login_attempt_counters (
                            dimension,
                            identifier,
                            window_started_at,
                            window_seconds,
                            attempt_count
                        )
                        VALUES (
                            'SOURCE',
                            :identifier,
                            statement_timestamp() - INTERVAL '3 days',
                            60,
                            1
                        )
                    """),
                    {"identifier": f"{prefix}{i}"},
                )

        deleted = cleanup_expired_login_counters(
            engine=engine,
            batch_size=2,
            max_batches=2,
        )

        assert deleted == 4

        with engine.connect() as connection:
            remaining = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_login_attempt_counters
                    WHERE identifier LIKE :prefix
                """),
                {"prefix": f"{prefix}%"},
            ).scalar_one()

        assert remaining == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE identifier LIKE :prefix
                """),
                {"prefix": f"{prefix}%"},
            )

def test_cleanup_skips_locked_counter(engine):
    locked_identifier = f"test-locked-{uuid.uuid4().hex}"
    expired_identifier = f"test-expired-{uuid.uuid4().hex}"

    identifiers = [locked_identifier, expired_identifier]

    try:
        with engine.begin() as connection:
            for identifier in identifiers:
                connection.execute(
                    text("""
                        INSERT INTO auth_login_attempt_counters (
                            dimension,
                            identifier,
                            window_started_at,
                            window_seconds,
                            attempt_count
                        )
                        VALUES (
                            'SOURCE',
                            :identifier,
                            statement_timestamp() - INTERVAL '3 days',
                            60,
                            1
                        )
                    """),
                    {"identifier": identifier},
                )

        with engine.begin() as locked_connection:
            locked_connection.execute(
                text("""
                    SELECT 1
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                    FOR UPDATE
                """),
                {"identifier": locked_identifier},
            ).all()

            deleted = cleanup_expired_login_counters(
                engine=engine,
                batch_size=500,
                max_batches=1,
            )

            assert deleted >= 1

            with engine.connect() as check_connection:
                locked_count = check_connection.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM auth_login_attempt_counters
                        WHERE dimension = 'SOURCE'
                          AND identifier = :identifier
                    """),
                    {"identifier": locked_identifier},
                ).scalar_one()

                expired_count = check_connection.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM auth_login_attempt_counters
                        WHERE dimension = 'SOURCE'
                          AND identifier = :identifier
                    """),
                    {"identifier": expired_identifier},
                ).scalar_one()

                assert locked_count == 1
                assert expired_count == 0

        deleted_after_unlock = cleanup_expired_login_counters(
            engine=engine,
            batch_size=500,
            max_batches=1,
        )

        with engine.connect() as connection:
            remaining = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": locked_identifier},
            ).scalar_one()

        assert deleted_after_unlock >= 1
        assert remaining == 0

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier IN (
                          :locked_identifier,
                          :expired_identifier
                      )
                """),
                {
                    "locked_identifier": locked_identifier,
                    "expired_identifier": expired_identifier,
                },
            )

def test_login_cleanup_does_not_delete_registration_counters(engine):
    import ipaddress

    client_ip = str(
        ipaddress.IPv4Address(
            0xC6336400 + (uuid.uuid4().int % 256)
        )
    )

    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO auth_registration_attempt_counters (
                        client_ip,
                        window_started_at,
                        window_seconds,
                        attempt_count
                    )
                    VALUES (
                        CAST(:client_ip AS inet),
                        statement_timestamp() - INTERVAL '3 days',
                        900,
                        1
                    )
                """),
                {"client_ip": client_ip},
            )

        cleanup_expired_login_counters(engine=engine)

        with engine.connect() as connection:
            remaining = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            ).scalar_one()

        assert remaining == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_cleanup_fails_when_database_unavailable(monkeypatch):
    class BrokenEngine:
        def begin(self):
            raise OperationalError(
                "SELECT 1",
                {},
                Exception("database unavailable"),
            )

    with pytest.raises(LoginCounterCleanupUnavailable):
        cleanup_expired_login_counters(
            engine=BrokenEngine(),
        )