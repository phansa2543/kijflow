import uuid, pytest, time
from datetime import timedelta, datetime, timezone
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text, create_engine
from sqlalchemy.pool import StaticPool

from app.auth.infrastructure.login_rate_limit import reserve_login_attempt, release_account_attempt, LoginLimiterUnavailable

def test_source_counter_rejects_attempt_over_limit(engine):
    identifier = f"test-source-{uuid.uuid4().hex}"

    try:

        results = [
                reserve_login_attempt(
                    engine,
                    dimension="SOURCE",
                    identifier=identifier,
                    window_seconds=60,
                    limit=3
                )
                for _ in range(4)
            ]

        assert [result.allowed for result in results] == [True, True, True, False]
        assert results[3].retry_after_seconds > 0

        with engine.begin() as connection:
            attempt_count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = 60
                """),
                {
                    "identifier": identifier,
                    "window_started_at": results[3].window_started_at
                }
            ).scalar_one()

        assert attempt_count == 4

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_account_counter_rejects_attempt_over_limit(engine):
    identifier = f"test-account-{uuid.uuid4().hex}"

    try:
        results = [
            reserve_login_attempt(
                engine=engine,
                dimension="ACCOUNT",
                identifier=identifier,
                window_seconds=900,
                limit=10
            )
            for _ in range(11)
        ]

        assert [result.allowed for result in results] == ([True] * 10 + [False])
        assert results[10].retry_after_seconds > 0

        with engine.connect() as connection:
            attempt_count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = 900
                """),
                {
                    "identifier": identifier,
                    "window_started_at": results[10].window_started_at
                }
            ).scalar_one()

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_release_account_attempt_decrements_once(engine):
    identifier = f"test-account-release-{uuid.uuid4().hex}"

    try:
        reservation = reserve_login_attempt(
            engine=engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=900,
            limit=10
        )

        assert reservation.allowed is True

        released = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds
        )

        assert released is True

        with engine.connect() as connection:
            attempt_count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = :window_seconds
                """),
                {
                    "identifier": identifier,
                    "window_started_at": reservation.window_started_at,
                    "window_seconds": reservation.window_seconds
                }
            ).scalar_one()

        assert attempt_count == 0

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_release_account_attempt_does_not_go_below_zero(engine):
    identifier = f"test-account-zero-{uuid.uuid4().hex}"

    try:
        reservation = reserve_login_attempt(
            engine=engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=900,
            limit=10
        )

        first_release = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds
        )

        second_release = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds
        )

        assert first_release is True
        assert second_release is False

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = :window_seconds
                """),
                {
                    "identifier": identifier,
                    "window_started_at": reservation.window_started_at,
                    "window_seconds": reservation.window_seconds
                }
            ).scalar_one()

        assert count == 0

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_release_account_attempt_does_not_affect_source(engine):
    identifier = f"test-source-release-{uuid.uuid4().hex}"

    try:
        reservation = reserve_login_attempt(
            engine=engine,
            dimension="SOURCE",
            identifier=identifier,
            window_seconds=60,
            limit=30
        )

        released = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds
        )

        assert released is False

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = :window_seconds
                """),
                {
                    "identifier": identifier,
                    "window_started_at": reservation.window_started_at,
                    "window_seconds": reservation.window_seconds
                }
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
                {"identifier": identifier}
            )

def test_release_account_attempt_does_not_affect_other_window(engine):
    identifier = f"test-account-window-{uuid.uuid4().hex}"

    try:
        reservation = reserve_login_attempt(
            engine=engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=900,
            limit=10
        )

        wrong_window = reservation.window_started_at + timedelta(seconds=900)

        released = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=wrong_window,
            window_seconds=reservation.window_seconds
        )

        assert released is False

        with engine.begin() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                    AND window_started_at = :window_started_at
                    AND window_seconds = :window_seconds
                """),
                {
                    "identifier": identifier,
                    "window_started_at": reservation.window_started_at,
                    "window_seconds": reservation.window_seconds
                }
            ).scalar_one()

        assert count == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_release_account_attempt_only_updates_reserved_window(engine):
    identifier = f"test-account-two-windows-{uuid.uuid4().hex}"

    try:
        reservation = reserve_login_attempt(
            engine=engine,
            dimension='ACCOUNT',
            identifier=identifier,
            window_seconds=900,
            limit=10
        )

        other_window = reservation.window_started_at + timedelta(seconds=900)

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
                        'ACCOUNT',
                        :identifier,
                        :window_started_at,
                        900,
                        3
                    )
                """),
                {
                    "identifier": identifier,
                    "window_started_at": other_window
                }
            )

        released = release_account_attempt(
            engine=engine,
            identifier=identifier,
            window_started_at=reservation.window_started_at,
            window_seconds=reservation.window_seconds
        )

        assert released is True

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT window_started_at, attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                    ORDER BY window_started_at
                """),
                {"identifier": identifier}
            ).all()

        counts = {row.window_started_at: row.attempt_count for row in rows}

        assert counts[reservation.window_started_at] == 0
        assert counts[other_window] == 3
        assert len(counts) == 2

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_concurrent_source_reservations_are_atomic(engine):
    identifier = f"test-source-concurrent-{uuid.uuid4().hex}"
    total_requests = 20

    try:
        def reserve():
            return reserve_login_attempt(
                engine,
                dimension="SOURCE",
                identifier=identifier,
                window_seconds=3600,
                limit=10
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: reserve(), range(total_requests)))

        assert sum(result.allowed for result in results) == 10
        assert sum(not result.allowed for result in results) == 10

        with engine.connect() as connection:
            total_count = connection.execute(
                text("""
                    SELECT SUM(attempt_count)
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            ).scalar_one()

        assert total_count == total_requests
        assert len({result.window_started_at for result in results}) == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                    AND identifier = :identifier
                """),
                {"identifier": identifier}
            )

def test_reserve_login_attempt_fails_closed_when_database_unavailable():
    broken_engine = create_engine(
        "postgresql+psycopg://invalid:invalid@127.0.0.1:1/invalid",
        connect_args={"connect_timeout": 1},
        poolclass=StaticPool,
    )

    try:
        with pytest.raises(LoginLimiterUnavailable):
            reserve_login_attempt(
                broken_engine,
                dimension="SOURCE",
                identifier="test-source-unavailable",
                window_seconds=60,
                limit=30,
            )
    finally:
        broken_engine.dispose()

def test_release_account_attempt_raises_when_database_unavailable():
    broken_engine = create_engine(
        "postgresql+psycopg://invalid:invalid@127.0.0.1:1/invalid",
        connect_args={"connect_timeout": 1},
        poolclass=StaticPool,
    )

    try:
        with pytest.raises(LoginLimiterUnavailable):
            release_account_attempt(
                broken_engine,
                identifier="test-account-unavailable",
                window_started_at=datetime.now(timezone.utc),
                window_seconds=900,
            )
    finally:
        broken_engine.dispose()

def test_concurrent_account_releases_do_not_underflow(engine):
    identifier = f"test-account-concurrent-release-{uuid.uuid4().hex}"
    total_releases = 20

    try:
        reservation = reserve_login_attempt(
            engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=900,
            limit=10,
        )

        def release():
            return release_account_attempt(
                engine,
                identifier=identifier,
                window_started_at=reservation.window_started_at,
                window_seconds=reservation.window_seconds,
            )

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(
                executor.map(lambda _: release(), range(total_releases))
            )

        assert sum(results) == 1
        assert results.count(False) == 19

        with engine.connect() as connection:
            count = connection.execute(
                text("""
                    SELECT attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                      AND identifier = :identifier
                      AND window_started_at = :window_started_at
                      AND window_seconds = :window_seconds
                """),
                {
                    "identifier": identifier,
                    "window_started_at": reservation.window_started_at,
                    "window_seconds": reservation.window_seconds,
                },
            ).scalar_one()

        assert count == 0

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE dimension = 'ACCOUNT'
                      AND identifier = :identifier
                """),
                {"identifier": identifier},
            )

def test_account_and_source_counters_are_independent(engine):
    identifier = f"test-dimensions-{uuid.uuid4().hex}"

    try:
        source = reserve_login_attempt(
            engine,
            dimension="SOURCE",
            identifier=identifier,
            window_seconds=60,
            limit=1,
        )

        account = reserve_login_attempt(
            engine,
            dimension="ACCOUNT",
            identifier=identifier,
            window_seconds=900,
            limit=1,
        )

        assert source.allowed is True
        assert account.allowed is True

        source_second = reserve_login_attempt(
            engine,
            dimension="SOURCE",
            identifier=identifier,
            window_seconds=60,
            limit=1,
        )

        assert source_second.allowed is False

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT dimension, SUM(attempt_count) AS total
                    FROM auth_login_attempt_counters
                    WHERE identifier = :identifier
                    GROUP BY dimension
                """),
                {"identifier": identifier},
            ).all()

        counts = {row.dimension: row.total for row in rows}

        assert counts["SOURCE"] == 2
        assert counts["ACCOUNT"] == 1

    finally:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    DELETE FROM auth_login_attempt_counters
                    WHERE identifier = :identifier
                """),
                {"identifier": identifier},
            )

def test_reservation_uses_new_fixed_window(engine):
    identifier = f"test-window-boundary-{uuid.uuid4().hex}"

    try:

        first = reserve_login_attempt(
            engine,
            dimension="SOURCE",
            identifier=identifier,
            window_seconds=1,
            limit=1,
        )

        while True:
            with engine.connect() as connection:
                changed = connection.execute(
                    text("""
                        SELECT clock_timestamp() >=
                            :window_started_at
                            + INTERVAL '1 second'
                    """),
                    {"window_started_at": first.window_started_at},
                ).scalar_one()

            if changed:
                break

            time.sleep(0.01)

        second = reserve_login_attempt(
            engine,
            dimension="SOURCE",
            identifier=identifier,
            window_seconds=1,
            limit=1,
        )

        assert second.window_started_at > first.window_started_at
        assert first.allowed is True
        assert second.allowed is True

        with engine.connect() as connection:
            rows = connection.execute(
                text("""
                    SELECT window_started_at, attempt_count
                    FROM auth_login_attempt_counters
                    WHERE dimension = 'SOURCE'
                      AND identifier = :identifier
                    ORDER BY window_started_at
                """),
                {"identifier": identifier},
            ).all()

        assert len(rows) == 2
        assert [row.attempt_count for row in rows] == [1, 1]

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