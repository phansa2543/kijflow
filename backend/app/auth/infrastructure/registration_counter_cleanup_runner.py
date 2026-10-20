from app.db.engine import create_database_engine

from app.auth.infrastructure.registration_counter_cleanup import (
    cleanup_expired_registration_counters,
)

RETENTION_SECONDS = 86_400
BATCH_SIZE = 500
MAX_BATCHES = 20


def main() -> None:
    engine = create_database_engine()

    try:
        total_deleted = 0

        for _ in range(MAX_BATCHES):
            deleted = cleanup_expired_registration_counters(
                engine=engine,
                retention_seconds=RETENTION_SECONDS,
                batch_size=BATCH_SIZE,
            )

            total_deleted += deleted

            if deleted < BATCH_SIZE:
                print(f"Cleanup completed: {total_deleted} rows")
                return

        print(
            f"Cleanup batch limit reached: {total_deleted} rows. "
            "Additional cleanup may be required."
        )

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()