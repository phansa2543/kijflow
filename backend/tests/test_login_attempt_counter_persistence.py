import uuid, pytest

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

def test_login_counter_accept_zero(db_connection):
    identifier = uuid.uuid4().hex

    db_connection.execute(
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
                TIMESTAMPTZ '2026-01-01 00:00:00+00',
                900,
                0
            )
        """),
        {"identifier": identifier}
    )

    count = db_connection.execute(
        text("""
            SELECT attempt_count
            FROM auth_login_attempt_counters
            WHERE dimension = 'ACCOUNT'
            AND identifier = :identifier
        """),
        {"identifier": identifier}
    ).scalar_one()

    assert count == 0

def test_login_counter_rejects_invalid_dimension(db_connection):
    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
                text("""
                    INSERT INTO auth_login_attempt_counters (
                        dimension,
                        identifier,
                        window_started_at,
                        window_seconds,
                        attempt_count
                    )
                    VALUES (
                        'INVALID',
                        :identifier,
                        TIMESTAMPTZ '2026-01-01 00:00:00+00',
                        900,
                        1
                    )
                """),
                {"identifier": uuid.uuid4().hex}
            )

def test_login_counter_rejects_empty_identifier(db_connection):
    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
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
                        '',
                        TIMESTAMPTZ '2026-01-01 00:00:00+00',
                        900,
                        1
                    )
                """)
            )

@pytest.mark.parametrize("window_seconds", [0, -1])
def test_login_counter_rejects_invalid_window_seconds(
    db_connection, window_seconds
):
    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
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
                        TIMESTAMPTZ '2026-01-01 00:00:00+00',
                        :window_seconds,
                        1
                    )
                """),
                {
                    "identifier": uuid.uuid4().hex,
                    "window_seconds": window_seconds
                }
            )

def test_login_counter_rejects_negative_attempt_count(db_connection):
    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
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
                        TIMESTAMPTZ '2026-01-01 00:00:00+00',
                        900,
                        -1
                    )
                """),
                {"identifier": uuid.uuid4().hex}
            )

def test_login_counter_rejects_duplicate__primary_key(db_connection):
    identifier = uuid.uuid4().hex

    insert_sql = text("""
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
                        TIMESTAMPTZ '2026-01-01 00:00:00+00',
                        900,
                        1
                    )
                """)

    db_connection.execute(insert_sql, {"identifier": identifier})

    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
                insert_sql,
                {"identifier": identifier}
            )

def test_login_counter_cleanup_index_exists(db_connection):
    index_exists = db_connection.execute(
        text("""
            SELECT EXISTS (
                SELECT 1
                FROM pg_indexes
                WHERE schemaname = current_schema()
                AND tablename = 'auth_login_attempt_counters'
                AND indexname = 'ix_auth_login_counter_window_started_at'
            )
        """)
    ).scalar_one()

    assert index_exists is True