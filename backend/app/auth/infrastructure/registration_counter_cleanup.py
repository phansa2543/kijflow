from sqlalchemy import text
from sqlalchemy.engine import Engine


def cleanup_expired_registration_counters(
    *,
    engine: Engine,
    retention_seconds: int = 86_400,
    batch_size: int = 500,
) -> int:
    if type(retention_seconds) is not int or retention_seconds < 0:
        raise ValueError("Invalid retention")

    if type(batch_size) is not int or not 1 <= batch_size <= 500:
        raise ValueError("Invalid batch size")

    statement = text("""
        WITH expired AS (
            SELECT ctid
            FROM auth_registration_attempt_counters
            WHERE window_started_at <
                statement_timestamp()
                - (:retention_seconds * INTERVAL '1 second')
              AND (
                window_started_at
                + (window_seconds * INTERVAL '1 second')
              ) <
                statement_timestamp()
                - (:retention_seconds * INTERVAL '1 second')
            ORDER BY window_started_at
            LIMIT :batch_size
            FOR UPDATE SKIP LOCKED
        )
        DELETE FROM auth_registration_attempt_counters AS counter
        USING expired
        WHERE counter.ctid = expired.ctid
        RETURNING 1
    """)

    with engine.begin() as connection:
        result = connection.execute(
            statement,
            {
                "retention_seconds": retention_seconds,
                "batch_size": batch_size,
            },
        )

        return len(result.all())