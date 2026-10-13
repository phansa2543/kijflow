import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

@pytest.fixture(scope="session")
def engine():
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL not set")

    if test_database_url == os.getenv("DATABASE_URL"):
        raise RuntimeError("TEST_DATABASE_URL must not use the development database")

    test_engine = create_engine(test_database_url)

    yield test_engine

    test_engine.dispose()

@pytest.fixture
def db_connection(engine):
    connection = engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()