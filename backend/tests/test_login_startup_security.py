import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

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
        with TestClient(app):
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