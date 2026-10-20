import uuid, pytest

from unittest.mock import MagicMock
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.auth.application.errors import RegistrationLimiterUnavailable

from app.auth.infrastructure.registration_rate_limit import (
    consume_registration_attempt,
)


def test_registration_rate_limit_counts_and_rejects(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    try:
        results = [
            consume_registration_attempt(
                engine=engine,
                client_ip=client_ip,
                threshold=2,
                window_seconds=3600,
            )
            for _ in range(3)
        ]

        assert [allowed for allowed, _ in results] == [
            True,
            True,
            False,
        ]

        assert 1 <= results[2][1] <= 3600

        with engine.connect() as connection:
            counts = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = 3600
                """),
                {"client_ip": client_ip},
            ).scalars().all()

        assert counts == [3]

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_registration_rate_limit_is_atomic_under_concurrency(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    total_attempts = 12
    threshold = 10
    window_seconds = 900

    barrier = Barrier(total_attempts)

    def attempt(_):
        barrier.wait(timeout=30)

        return consume_registration_attempt(
            engine=engine,
            client_ip=client_ip,
            threshold=threshold,
            window_seconds=window_seconds,
        )

    try:
        with ThreadPoolExecutor(
            max_workers=total_attempts
        ) as executor:
            results = list(
                executor.map(attempt, range(total_attempts))
            )

        allowed_count = sum(
            1 for allowed, _ in results if allowed
        )

        rejected_count = sum(
            1 for allowed, _ in results if not allowed
        )

        assert allowed_count == 10
        assert rejected_count == 2

        with engine.connect() as connection:
            counts = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = :window_seconds
                """),
                {
                    "client_ip": client_ip,
                    "window_seconds": window_seconds,
                },
            ).scalars().all()

        assert counts == [12]

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_registration_rate_limit_uses_postgresql_time(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    window_seconds = 900

    db_window_query = text("""
        SELECT to_timestamp(
            floor(
                extract(epoch FROM clock_timestamp())
                / :window_seconds
            ) * :window_seconds
        )
    """)

    try:
        with engine.connect() as connection:
            window_before = connection.execute(
                db_window_query,
                {"window_seconds": window_seconds},
            ).scalar_one()

        allowed, retry_after = consume_registration_attempt(
            engine=engine,
            client_ip=client_ip,
            threshold=10,
            window_seconds=window_seconds,
        )

        with engine.connect() as connection:
            window_after = connection.execute(
                db_window_query,
                {"window_seconds": window_seconds},
            ).scalar_one()

            counter = connection.execute(
                text("""
                    SELECT window_started_at, attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = :window_seconds
                """),
                {
                    "client_ip": client_ip,
                    "window_seconds": window_seconds,
                },
            ).one()

        assert allowed is True
        assert counter.attempt_count == 1

        assert counter.window_started_at in (
            window_before,
            window_after,
        )

        assert 1 <= retry_after <= window_seconds

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_registration_rate_limit_resets_after_previous_window(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    threshold = 10
    window_seconds = 900

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
                    SELECT
                        CAST(:client_ip AS inet),
                        to_timestamp(
                            floor(
                                extract(epoch FROM clock_timestamp())
                                / :window_seconds
                            ) * :window_seconds
                        ) - (:window_seconds * INTERVAL '1 second'),
                        :window_seconds,
                        :attempt_count
                """),
                {
                    "client_ip": client_ip,
                    "window_seconds": window_seconds,
                    "attempt_count": threshold + 1,
                },
            )

        allowed, retry_after = consume_registration_attempt(
            engine=engine,
            client_ip=client_ip,
            threshold=threshold,
            window_seconds=window_seconds,
        )

        assert allowed is True
        assert 1 <= retry_after <= window_seconds

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT window_started_at, attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = :window_seconds
                    ORDER BY window_started_at
                """),
                {
                    "client_ip": client_ip,
                    "window_seconds": window_seconds,
                },
            ).all()

        assert len(rows) == 2
        assert rows[0].attempt_count == 11
        assert rows[1].attempt_count == 1
        assert rows[1].window_started_at > rows[0].window_started_at

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_registration_quota_survives_separate_transaction_rollback(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

    try:
        with pytest.raises(RuntimeError, match="Simulated rollback"):
            with engine.begin() as registration_connection:
                registration_connection.execute(text("SELECT 1"))

                allowed, _ = consume_registration_attempt(
                    engine=engine,
                    client_ip=client_ip,
                    threshold=10,
                    window_seconds=900,
                )

                assert allowed is True

                raise RuntimeError("Simulated rollback")

        with engine.connect() as connection:
            counts = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                      AND window_seconds = 900
                """),
                {"client_ip": client_ip},
            ).scalars().all()

        assert counts == [1]

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip = CAST(:client_ip AS inet)
                """),
                {"client_ip": client_ip},
            )

def test_registration_rate_limit_isolated_by_client_ip(engine):
    assert engine.url.database == "kijflow_test"

    def unique_ip():
        suffix = uuid.uuid4().hex[:24]
        groups = ":".join(
            suffix[i:i + 4] for i in range(0, 24, 4)
        )
        return f"2001:db8:{groups}"

    ip_a = unique_ip()
    ip_b = unique_ip()

    try:
        results_a = [
            consume_registration_attempt(
                engine=engine,
                client_ip=ip_a,
                threshold=2,
                window_seconds=900,
            )
            for _ in range(3)
        ]

        result_b = consume_registration_attempt(
            engine=engine,
            client_ip=ip_b,
            threshold=2,
            window_seconds=900,
        )

        assert [allowed for allowed, _ in results_a] == [
            True, True, False
        ]

        assert result_b[0] is True

        with engine.connect() as connection:
            counts = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_registration_attempt_counters
                    WHERE client_ip IN (
                        CAST(:ip_a AS inet),
                        CAST(:ip_b AS inet)
                    )
                    AND window_seconds = 900
                    ORDER BY attempt_count
                """),
                {"ip_a": ip_a, "ip_b": ip_b},
            ).scalars().all()

        assert counts == [1, 3]

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip IN (
                        CAST(:ip_a AS inet),
                        CAST(:ip_b AS inet)
                    )
                """),
                {"ip_a": ip_a, "ip_b": ip_b},
            )

def test_registration_rate_limit_fails_closed_on_database_error():
    engine = MagicMock()

    database_error = OperationalError(
        "INSERT INTO auth_registration_attempt_counters",
        {},
        RuntimeError("Sensitive database details"),
    )

    engine.begin.return_value.__enter__.return_value.execute.side_effect = (
        database_error
    )

    with pytest.raises(RegistrationLimiterUnavailable) as exc_info:
        consume_registration_attempt(
            engine=engine,
            client_ip="192.0.2.10",
            threshold=10,
            window_seconds=900,
        )

    assert str(exc_info.value) == "Registration limiter unavailable"
    assert "Sensitive database details" not in str(exc_info.value)

    engine.begin.assert_called_once_with()
    engine.begin.return_value.__enter__.return_value.execute.assert_called_once()