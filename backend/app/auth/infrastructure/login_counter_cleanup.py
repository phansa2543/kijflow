from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


LOGIN_COUNTER_RETENTION_SECONDS = 86_400
LOGIN_COUNTER_CLEANUP_BATCH_SIZE = 500
LOGIN_COUNTER_CLEANUP_MAX_BATCHES = 20


class LoginCounterCleanupUnavailable(Exception):
    """Login counter cleanup persistence is unavailable."""


def cleanup_expired_login_counters(
    *,
    engine: Engine,
    retention_seconds: int = LOGIN_COUNTER_RETENTION_SECONDS,
    batch_size: int = LOGIN_COUNTER_CLEANUP_BATCH_SIZE,
    max_batches: int = LOGIN_COUNTER_CLEANUP_MAX_BATCHES,
) -> int:
    if type(retention_seconds) is not int or retention_seconds < 0:
        raise ValueError("Invalid retention")

    if type(batch_size) is not int or not 1 <= batch_size <= 500:
        raise ValueError("Invalid batch size")

    if type(max_batches) is not int or not 1 <= max_batches <= 20:
        raise ValueError("Invalid max batches")

    statement = text("""
        WITH expired AS (
            SELECT ctid
            FROM auth_login_attempt_counters
            WHERE (
                window_started_at
                + (window_seconds * INTERVAL '1 second')
            ) < statement_timestamp()
                - (:retention_seconds * INTERVAL '1 second')
            ORDER BY window_started_at
            LIMIT :batch_size
            FOR UPDATE SKIP LOCKED
        )
        DELETE FROM auth_login_attempt_counters AS counter
        USING expired
        WHERE counter.ctid = expired.ctid
        RETURNING 1
    """)

    total_deleted = 0

    try:
        for _ in range(max_batches):
            with engine.begin() as connection:
                deleted_rows = connection.execute(
                    statement,
                    {
                        "retention_seconds": retention_seconds,
                        "batch_size": batch_size,
                    },
                ).all()

                deleted_count = len(deleted_rows)

            total_deleted += deleted_count

            if deleted_count < batch_size:
                break

    except SQLAlchemyError as exc:
        raise LoginCounterCleanupUnavailable(
            "login counter cleanup unavailable"
        ) from exc

    return total_deleted