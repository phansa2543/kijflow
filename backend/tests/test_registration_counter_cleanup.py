import uuid
import pytest

from unittest.mock import Mock, patch

from app.auth.infrastructure.registration_counter_cleanup_runner import main

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import text

from app.auth.infrastructure.registration_counter_cleanup import (
    cleanup_expired_registration_counters,
)


def test_cleanup_removes_expired_but_preserves_active(engine):
    assert engine.url.database == "kijflow_test"

    def unique_ip():
        suffix = uuid.uuid4().hex[:24]
        groups = ":".join(
            suffix[i:i + 4] for i in range(0, 24, 4)
        )
        return f"2001:db8:{groups}"

    expired_ip = unique_ip()
    active_ip = unique_ip()

    insert_statement = text("""
        INSERT INTO auth_registration_attempt_counters (
            client_ip,
            window_started_at,
            window_seconds,
            attempt_count
        )
        VALUES (
            CAST(:client_ip AS inet),
            to_timestamp(
                floor(extract(epoch FROM clock_timestamp()) / 900) * 900
            ) - (:days_old * INTERVAL '1 day'),
            900,
            1
        )
    """)

    try:
        with engine.begin() as connection:
            for ip, days_old in [
                (expired_ip, 3),
                (active_ip, 0),
            ]:
                connection.execute(
                    insert_statement,
                    {"client_ip": ip, "days_old": days_old},
                )

        deleted = cleanup_expired_registration_counters(
            engine=engine,
            retention_seconds=86_400,
            batch_size=500,
        )

        with engine.connect() as connection:
            def count_rows(ip):
                return connection.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                    """),
                    {"client_ip": ip},
                ).scalar_one()

            assert count_rows(expired_ip) == 0
            assert count_rows(active_ip) == 1

        assert deleted >= 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_registration_attempt_counters
                    WHERE client_ip IN (
                        CAST(:expired_ip AS inet),
                        CAST(:active_ip AS inet)
                    )
                """),
                {
                    "expired_ip": expired_ip,
                    "active_ip": active_ip,
                },
            )

def test_cleanup_respects_batch_size(engine):
    assert engine.url.database == "kijflow_test"

    ips = []

    for _ in range(3):
        suffix = uuid.uuid4().hex[:24]
        groups = ":".join(
            suffix[i:i + 4]
            for i in range(0, 24, 4)
        )
        ips.append(f"2001:db8:{groups}")

    try:
        with engine.begin() as connection:
            for ip in ips:
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
                            clock_timestamp() - INTERVAL '3 days',
                            900,
                            1
                        )
                    """),
                    {"client_ip": ip},
                )

        with engine.connect() as connection:
            before = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_registration_attempt_counters
                """)
            ).scalar_one()

        deleted = cleanup_expired_registration_counters(
            engine=engine,
            retention_seconds=86_400,
            batch_size=2,
        )

        with engine.connect() as connection:
            after = connection.execute(
                text("""
                    SELECT COUNT(*)
                    FROM auth_registration_attempt_counters
                """)
            ).scalar_one()

        assert deleted == 2
        assert before - after == 2

    finally:
        with engine.begin() as connection:
            for ip in ips:
                connection.execute(
                    text("""
                        DELETE FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                    """),
                    {"client_ip": ip},
                )

def test_cleanup_skips_locked_rows(engine):
    assert engine.url.database == "kijflow_test"

    def unique_ip():
        suffix = uuid.uuid4().hex[:24]
        groups = ":".join(
            suffix[i:i + 4] for i in range(0, 24, 4)
        )
        return f"2001:db8:{groups}"

    locked_ip = unique_ip()
    expired_ip = unique_ip()
    active_ip = unique_ip()

    try:
        with engine.begin() as connection:
            for ip, days_old in [
                (locked_ip, 3),
                (expired_ip, 3),
                (active_ip, 0),
            ]:
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
                            clock_timestamp()
                                - (:days_old * INTERVAL '1 day'),
                            900,
                            1
                        )
                    """),
                    {"client_ip": ip, "days_old": days_old},
                )

        with engine.connect() as locker:
            with locker.begin():
                locker.execute(
                    text("""
                        SELECT client_ip
                        FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                        FOR UPDATE
                    """),
                    {"client_ip": locked_ip},
                ).all()

                deleted = cleanup_expired_registration_counters(
                    engine=engine,
                    retention_seconds=86_400,
                    batch_size=500,
                )

                with engine.connect() as check:
                    def exists(ip):
                        return check.execute(
                            text("""
                                SELECT EXISTS (
                                    SELECT 1
                                    FROM auth_registration_attempt_counters
                                    WHERE client_ip = CAST(:client_ip AS inet)
                                )
                            """),
                            {"client_ip": ip},
                        ).scalar_one()

                    assert exists(locked_ip) is True
                    assert exists(expired_ip) is False
                    assert exists(active_ip) is True

                assert deleted >= 1

    finally:
        with engine.begin() as connection:
            for ip in [locked_ip, expired_ip, active_ip]:
                connection.execute(
                    text("""
                        DELETE FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                    """),
                    {"client_ip": ip},
                )

def test_cleanup_with_two_workers(engine):
    assert engine.url.database == "kijflow_test"

    def unique_ip():
        suffix = uuid.uuid4().hex[:24]
        groups = ":".join(
            suffix[i:i + 4] for i in range(0, 24, 4)
        )
        return f"2001:db8:{groups}"

    ips = [unique_ip() for _ in range(4)]

    try:
        with engine.begin() as connection:
            for ip in ips:
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
                            TIMESTAMPTZ '2000-01-01 00:00:00+00',
                            900,
                            1
                        )
                    """),
                    {"client_ip": ip},
                )

        barrier = Barrier(2)

        def worker(_):
            barrier.wait(timeout=10)

            return cleanup_expired_registration_counters(
                engine=engine,
                retention_seconds=86_400,
                batch_size=2,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(worker, range(2)))

        assert sorted(results) == [2, 2]

        with engine.connect() as connection:
            for ip in ips:
                remaining = connection.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                    """),
                    {"client_ip": ip},
                ).scalar_one()

                assert remaining == 0

    finally:
        with engine.begin() as connection:
            for ip in ips:
                connection.execute(
                    text("""
                        DELETE FROM auth_registration_attempt_counters
                        WHERE client_ip = CAST(:client_ip AS inet)
                    """),
                    {"client_ip": ip},
                )

def test_cleanup_runner_propagates_failure():
    engine = Mock()

    with (
        patch(
            "app.auth.infrastructure.registration_counter_cleanup_runner.create_database_engine",
            return_value=engine,
        ),
        patch(
            "app.auth.infrastructure.registration_counter_cleanup_runner.cleanup_expired_registration_counters",
            side_effect=RuntimeError("Simulated cleanup failure"),
        ) as cleanup,
    ):
        with pytest.raises(RuntimeError, match="Simulated cleanup failure"):
            main()

    cleanup.assert_called_once_with(
        engine=engine,
        retention_seconds=86_400,
        batch_size=500,
    )

    engine.dispose.assert_called_once()

def test_cleanup_runner_stops_at_batch_cap(capsys):
    engine = Mock()

    with (
        patch(
            "app.auth.infrastructure.registration_counter_cleanup_runner.create_database_engine",
            return_value=engine,
        ),
        patch(
            "app.auth.infrastructure.registration_counter_cleanup_runner.cleanup_expired_registration_counters",
            return_value=500,
        ) as cleanup,
    ):
        main()

    assert cleanup.call_count == 20

    cleanup.assert_called_with(
        engine=engine,
        retention_seconds=86_400,
        batch_size=500,
    )

    output = capsys.readouterr().out

    assert "Cleanup batch limit reached" in output
    assert "10000 rows" in output
    assert "Additional cleanup may be required" in output
    assert "Cleanup completed" not in output

    engine.dispose.assert_called_once()

def test_cleanup_preserves_counter_within_retention(engine):
    assert engine.url.database == "kijflow_test"

    suffix = uuid.uuid4().hex[:24]
    groups = ":".join(
        suffix[i:i + 4] for i in range(0, 24, 4)
    )
    client_ip = f"2001:db8:{groups}"

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
                        statement_timestamp()
                            - INTERVAL '24 hours',
                        900,
                        1
                    )
                """),
                {"client_ip": client_ip},
            )

        cleanup_expired_registration_counters(
            engine=engine,
            retention_seconds=86_400,
            batch_size=500,
        )

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