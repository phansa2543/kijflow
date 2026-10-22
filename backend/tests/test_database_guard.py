import pytest

from tests.database_guard import validate_test_database_url


DEV_URL = "postgresql+psycopg://user:password@localhost:5432/kijflow"
TEST_URL = "postgresql+psycopg://user:password@localhost:5432/kijflow_test"


def validate(test_url, dev_url):
    validate_test_database_url(
        test_database_url=test_url,
        development_database_url=dev_url,
    )


def test_rejects_missing_test_database_url():
    with pytest.raises(RuntimeError, match="TEST_DATABASE_URL not set"):
        validate(None, DEV_URL)


def test_rejects_missing_development_database_url():
    with pytest.raises(RuntimeError, match="DATABASE_URL not set"):
        validate(TEST_URL, None)


def test_rejects_test_url_targeting_development_database():
    with pytest.raises(RuntimeError, match="must target kijflow_test"):
        validate(DEV_URL, DEV_URL)


def test_rejects_same_database_name():
    with pytest.raises(RuntimeError, match="database names must differ"):
        validate(TEST_URL, TEST_URL)


def test_rejects_same_database_with_different_hosts():
    dev_url = "postgresql+psycopg://user:password@localhost:5432/kijflow_test"
    test_url = "postgresql+psycopg://user:password@127.0.0.1:5432/kijflow_test"

    with pytest.raises(RuntimeError, match="database names must differ"):
        validate(test_url, dev_url)


def test_rejects_sqlite_database():
    with pytest.raises(RuntimeError, match="must use PostgreSQL"):
        validate("sqlite:///kijflow_test", DEV_URL)


def test_accepts_separate_test_database():
    validate(TEST_URL, DEV_URL)