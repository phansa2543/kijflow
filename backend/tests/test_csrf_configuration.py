import pytest

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