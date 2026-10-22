from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


def validate_test_database_url(
    *,
    test_database_url: str | None,
    development_database_url: str | None,
) -> None:
    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL not set")

    if not development_database_url:
        raise RuntimeError("DATABASE_URL not set")

    try:
        test_url = make_url(test_database_url)
        development_url = make_url(development_database_url)
    except (ArgumentError, ValueError):
        raise RuntimeError(
            "Invalid database URL configuration"
        ) from None

    if test_url.get_backend_name() != "postgresql":
        raise RuntimeError("Test database must use PostgreSQL")

    if test_url.database != "kijflow_test":
        raise RuntimeError(
            "TEST_DATABASE_URL must target kijflow_test"
        )

    if development_url.database == test_url.database:
        raise RuntimeError(
            "Test and development database names must differ"
        )