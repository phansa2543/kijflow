import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from tests.database_guard import validate_test_database_url

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

@pytest.fixture(scope="session")
def engine():
    test_database_url = os.getenv("TEST_DATABASE_URL")
    development_database_url = os.getenv("DATABASE_URL")

    validate_test_database_url(
        test_database_url=test_database_url,
        development_database_url=development_database_url
    )

    test_engine = create_engine(test_database_url)

    try:
        with test_engine.connect() as connection:
            actual_database = connection.exec_driver_sql(
                "SELECT current_database()"
            ).scalar_one()

        if actual_database != "kijflow_test":
            raise RuntimeError("connected database is not kijflow_test")

        yield test_engine
    finally:
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