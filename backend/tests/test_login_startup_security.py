import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from app.main import app

@pytest.mark.parametrize(
    "secret",
    [None, "", "abc", "z" * 64,
    ],
)
def test_startup_rejects_invalid_login_hmac_secret(secret, monkeypatch):
    if secret is None:
        monkeypatch.delenv("LOGIN_COUNTER_HMAC_SECRET", raising=False)
    else:
        monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", secret)

    with pytest.raises(ValueError, match="invalid login counter HMAC configuration"):
        with patch("app.main.load_dotenv"), TestClient(app):
            pass

def test_startup_accepts_valid_login_hmac_secret(monkeypatch):
    monkeypatch.setenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        "a1" * 32,
    )

    with patch("app.main.create_database_engine") as create_engine:
        with TestClient(app):
            pass

    create_engine.assert_called_once_with()

    create_engine.return_value.dispose.assert_called_once()

def test_startup_loads_valid_secret_from_dotenv(
    monkeypatch,
    tmp_path,
):
    env_file = tmp_path / ".env"
    env_file.write_text(
        'LOGIN_COUNTER_HMAC_SECRET=' + ('a1' * 32) + '\n',
        encoding="utf-8",
    )

    monkeypatch.delenv(
        "LOGIN_COUNTER_HMAC_SECRET",
        raising=False,
    )

    with (
        patch("app.main.load_dotenv") as load_env,
        patch("app.main.create_database_engine") as create_engine,
    ):
        load_env.side_effect = lambda path: load_dotenv(env_file)

        with TestClient(app):
            pass

    create_engine.assert_called_once_with()
    create_engine.return_value.dispose.assert_called_once()