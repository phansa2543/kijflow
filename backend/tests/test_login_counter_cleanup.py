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
    identifier = f"test-locked-{uuid.uuid4().hex}"

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

        with engine.begin() as locked_connection:
            locked_connection.execute(
                text("""
                    SELECT 1
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                    FOR UPDATE
                """),
                {"identifier": identifier},
            )

            def set_cleanup_timeout(conn, cursor, statement, parameters, context, executemany):
                if statement.lstrip().upper().startswith("WITH EXPIRED AS"):
                    cursor.execute("SET LOCAL lock_timeout = '200ms'")

            event.listen(engine, "before_cursor_execute", set_cleanup_timeout)

            try:
                cleanup_expired_login_counters(
                    engine=engine,
                    batch_size=500,
                    max_batches=1,
                )
            finally:
                event.remove(engine, "before_cursor_execute", set_cleanup_timeout)

            count = locked_connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            ).scalar_one()

            assert count == 1

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