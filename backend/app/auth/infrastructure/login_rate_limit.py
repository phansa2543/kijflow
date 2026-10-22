from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

LoginCounterDimension = Literal["ACCOUNT", "SOURCE"]

@dataclass(frozen=True)
class LoginAttemptReservation:
    allowed: bool
    retry_after_seconds: int
    window_started_at: datetime
    window_seconds: int

class LoginLimiterUnavailable(Exception):
    """Login counter persistence is unavailable."""

def reserve_login_attempt(
        engine: Engine,
        *,
        dimension: LoginCounterDimension,
        identifier: str,
        window_seconds: int,
        limit: int
) -> LoginAttemptReservation:
    if dimension not in ("ACCOUNT", "SOURCE"):
        raise ValueError("invalid login counter dimension")
    
    if not identifier:
        raise ValueError("identifier must not be empty")

    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")

    if limit <= 0:
        raise ValueError("limit must be positive")

    statement = text("""
                WITH observed AS (
                    SELECT clock_timestamp() AS observed_at
                ),
                current_window AS (
                    SELECT
                        to_timestamp(
                            floor(
                                extract(epoch FROM observed_at) / :window_seconds
                            ) * :window_seconds
                        ) AS window_started_at,
                        observed_at
                    FROM observed
                ),
                reserved AS (
                    INSERT INTO auth_login_attempt_counters (
                        dimension,
                        identifier,
                        window_started_at,
                        window_seconds,
                        attempt_count
                    )
                    SELECT
                        :dimension,
                        :identifier,
                        window_started_at,
                        :window_seconds,
                        1
                    FROM current_window
                    ON CONFLICT (
                        dimension,
                        identifier,
                        window_started_at,
                        window_seconds
                    )
                    DO UPDATE SET
                        attempt_count = auth_login_attempt_counters.attempt_count + 1
                    RETURNING window_started_at, attempt_count
                )
                SELECT
                    reserved.window_started_at,
                    reserved.attempt_count,
                    GREATEST(
                        0,
                        CEIL(
                            EXTRACT(
                                EPOCH FROM (
                                    reserved.window_started_at
                                    + (:window_seconds * INTERVAL '1 second')
                                    - current_window.observed_at
                                )
                            )
                        )
                    )::integer AS retry_after_seconds
                FROM reserved
                CROSS JOIN current_window
            """)

    try:
        with engine.begin() as connection:
            row = connection.execute(
                statement,
                {
                    "dimension": dimension,
                    "identifier": identifier,
                    "window_seconds": window_seconds
                }
            ).one()

        attempt_count = row.attempt_count

        return LoginAttemptReservation(
            allowed=attempt_count <= limit,
            retry_after_seconds=(
                0 if attempt_count <= limit else row.retry_after_seconds
            ),
            window_started_at=row.window_started_at,
            window_seconds=window_seconds
        )

    except SQLAlchemyError as exc:
        raise LoginLimiterUnavailable(
            "login counter persistence unavailable"
        ) from exc

def release_account_attempt(
        engine: Engine,
        *,
        identifier: str,
        window_started_at: datetime,
        window_seconds: int
) -> bool:
    if not identifier:
        raise ValueError("identifier must not be empty")

    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")

    statement = text("""
            UPDATE auth_login_attempt_counters
            SET attempt_count = attempt_count - 1
            WHERE dimension = 'ACCOUNT'
            AND identifier = :identifier
            AND window_started_at = :window_started_at
            AND window_seconds = :window_seconds
            AND attempt_count > 0
            RETURNING attempt_count
        """)

    try:
        with engine.begin() as connection:
            row = connection.execute(
                statement,
                {
                    "identifier": identifier,
                    "window_started_at": window_started_at,
                    "window_seconds": window_seconds
                }
            ).first()

        return row is not None

    except SQLAlchemyError as exc:
        raise LoginLimiterUnavailable(
            "login counter persistence unavailable"
        ) from exc