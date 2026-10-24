import pytest

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

from app.auth.presentation.csrf import normalize_trusted_origin


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:3100",
        "http://127.0.0.1:5173",
        "https://app.kijflow.com",
    ],
)
def test_valid_runtime_origins(origin):
    assert normalize_trusted_origin(origin) == origin


@pytest.mark.parametrize(
    "origin",
    [
        "",
        "null",
        "http://app.kijflow.com",
        "https://app.kijflow.com/",
        "https://app.kijflow.com/path",
        "https://app.kijflow.com.",
        "https://app.kijflow.com:0",
    ],
)
def test_invalid_runtime_origins(origin):
    with pytest.raises(ValueError):
        normalize_trusted_origin(origin)

def test_missing_trusted_origin_fails_before_engine(monkeypatch):
    monkeypatch.delenv("TRUSTED_FRONTEND_ORIGIN", raising=False)

    with (
        patch("app.main.load_dotenv"),
        patch("app.main.create_database_engine") as create_engine,
    ):
        with pytest.raises(
            ValueError,
            match="Missing configuration: TRUSTED_FRONTEND_ORIGIN",
        ):
            with TestClient(app):
                pass

    create_engine.assert_not_called()


@pytest.mark.parametrize(
    "invalid_origin",
    [
        "",
        "null",
        "https://evil.example/path",
        "http://app.kijflow.com",
    ],
)
def test_invalid_trusted_origin_fails_before_engine(
    monkeypatch, invalid_origin
):
    monkeypatch.setenv(
        "TRUSTED_FRONTEND_ORIGIN",
        invalid_origin,
    )

    with (
        patch("app.main.load_dotenv"),
        patch("app.main.create_database_engine") as create_engine,
    ):
        with pytest.raises(ValueError, match="Invalid trusted frontend origin|HTTP trusted origin must be local"):
            with TestClient(app):
                pass

    create_engine.assert_not_called()