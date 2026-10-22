from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


CONFIG = {
    "LOGIN_SOURCE_LIMIT": "5",
    "LOGIN_SOURCE_WINDOW_SECONDS": "120",
    "LOGIN_ACCOUNT_LIMIT": "3",
    "LOGIN_ACCOUNT_WINDOW_SECONDS": "300",
}


def test_custom_login_config_loaded(monkeypatch):
    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", "a1" * 32)

    for name, value in CONFIG.items():
        monkeypatch.setenv(name, value)

    with patch("app.main.create_database_engine"):
        with TestClient(app):
            assert app.state.login_source_limit == 5
            assert app.state.login_source_window_seconds == 120
            assert app.state.login_account_limit == 3
            assert app.state.login_account_window_seconds == 300


@pytest.mark.parametrize(
    "invalid_value",
    ["0", "-1", "abc"],
)
@pytest.mark.parametrize("config_name", CONFIG.keys())
def test_invalid_login_config_fails_before_engine(
    monkeypatch,
    config_name,
    invalid_value,
):
    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", "a1" * 32)

    for name, value in CONFIG.items():
        monkeypatch.setenv(name, value)

    monkeypatch.setenv(config_name, invalid_value)

    with patch("app.main.create_database_engine") as create_engine:
        with pytest.raises(ValueError, match="Invalid configuration"):
            with TestClient(app):
                pass

        create_engine.assert_not_called()

def test_default_login_config(monkeypatch):
    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", "a1" * 32)

    for name in CONFIG:
        monkeypatch.delenv(name, raising=False)

    with patch("app.main.create_database_engine"):
        with TestClient(app):
            assert app.state.login_source_limit == 30
            assert app.state.login_source_window_seconds == 60
            assert app.state.login_account_limit == 10
            assert app.state.login_account_window_seconds == 900