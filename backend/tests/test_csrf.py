import pytest

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.presentation.csrf import (
    normalize_trusted_origin,
    require_trusted_origin,
)


@pytest.mark.parametrize(
    ("origin", "expected"),
    [
        ("http://localhost:3000", "http://localhost:3000"),
        ("http://localhost:3100", "http://localhost:3100"),
        ("http://127.0.0.1:5173", "http://127.0.0.1:5173"),
        ("https://app.kijflow.com", "https://app.kijflow.com"),
        ("HTTPS://APP.KIJFLOW.COM", "https://app.kijflow.com"),
    ],
)
def test_normalize_valid_trusted_origin(origin, expected):
    assert normalize_trusted_origin(origin) == expected


@pytest.mark.parametrize(
    "origin",
    [
        "",
        "null",
        "localhost:3000",
        "https://",
        "https://app.kijflow.com/path",
        "https://app.kijflow.com?x=1",
        "https://app.kijflow.com#fragment",
        "https://user@app.kijflow.com",
        "https://app.kijflow.com:invalid",
        "https://app.kijflow.com ",
        "http://app.kijflow.com",
        "https://evil.com@trusted.com",
    ],
)
def test_reject_invalid_trusted_origin(origin):
    with pytest.raises(ValueError):
        normalize_trusted_origin(origin)


@pytest.fixture
def client():
    app = FastAPI()
    app.state.trusted_frontend_origin = "http://localhost:3100"

    @app.post("/test-csrf", dependencies=[Depends(require_trusted_origin)])
    def test_endpoint():
        return {"ok": True}

    with TestClient(app) as test_client:
        yield test_client


def test_accept_trusted_origin(client):
    response = client.post(
        "/test-csrf",
        headers={"Origin": "http://localhost:3100"},
    )

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:3000",
        "http://127.0.0.1:3100",
        "https://evil.example",
        "null",
        "http://localhost:3100.evil.example",
    ],
)
def test_reject_untrusted_origin(client, origin):
    response = client.post(
        "/test-csrf",
        headers={"Origin": origin},
    )

    assert response.status_code == 403


def test_reject_missing_origin(client):
    response = client.post("/test-csrf")

    assert response.status_code == 403


def test_reject_duplicate_origin_headers(client):
    response = client.post(
        "/test-csrf",
        headers=[
            ("Origin", "http://localhost:3100"),
            ("Origin", "https://evil.example"),
        ],
    )

    assert response.status_code == 403

@pytest.mark.parametrize(
    "origin",
    [
        r"https://app.kijflow.com\@evil.example",
        "https://app.kijflow.com%2Fevil.example",
        "https://app.kijflow.com.",
        "https://app.kijflow.com:443:444",
        "https://app.kijflow.com, https://evil.example",
        "https://app.kijflow.com\nX-Injected: value",
        "https://app.kijflow.com:0",
        "https://app.kijflow.com:65536",
    ],
)
def test_reject_ambiguous_or_malformed_origin(origin):
    with pytest.raises(ValueError):
        normalize_trusted_origin(origin)