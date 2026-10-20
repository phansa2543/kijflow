from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.auth.application.errors import RegistrationLimiterUnavailable

def consume_registration_attempt(
    *,
    engine: Engine,
    client_ip: str,
    threshold: int,
    window_seconds: int,
) -> tuple[bool, int]:
    if threshold < 1 or window_seconds < 1:
        raise ValueError("Invalid registration rate limit configuration")

    statement = text("""
        WITH db_clock AS (
            SELECT clock_timestamp() AS observed_at
        ),
        current_window AS (
            SELECT
                observed_at,
                to_timestamp(
                    floor(
                        extract(epoch FROM observed_at)
                        / :window_seconds
                    ) * :window_seconds
                ) AS window_started_at
            FROM db_clock
        ),
        counter AS (
            INSERT INTO auth_registration_attempt_counters (
                client_ip,
                window_started_at,
                window_seconds,
                attempt_count
            )
            SELECT
                CAST(:client_ip AS inet),
                window_started_at,
                :window_seconds,
                1
            FROM current_window
            ON CONFLICT (
                client_ip,
                window_started_at,
                window_seconds
            )
            DO UPDATE SET
                attempt_count =
                    auth_registration_attempt_counters.attempt_count + 1
            RETURNING attempt_count
        )
        SELECT
            counter.attempt_count <= :threshold AS allowed,
            GREATEST(
                1,
                CEIL(
                    EXTRACT(
                        EPOCH FROM (
                            current_window.window_started_at
                            + (:window_seconds * INTERVAL '1 second')
                            - current_window.observed_at
                        )
                    )
                )::integer
            ) AS retry_after_seconds
        FROM counter
        CROSS JOIN current_window
    """)
    try:
        with engine.begin() as connection:
            result = connection.execute(
                statement,
                {
                    "client_ip": client_ip,
                    "threshold": threshold,
                    "window_seconds": window_seconds,
                },
            ).one()
    except SQLAlchemyError:
        raise RegistrationLimiterUnavailable(
            "Registration limiter unavailable"
        ) from None

    return bool(result.allowed), int(result.retry_after_seconds)