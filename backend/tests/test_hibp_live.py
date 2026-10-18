import os, httpx, pytest

from app.auth.hibp import is_password_compromised

@pytest.mark.skipif(
    os.getenv("RUN_LIVE_HIBP") != "1",
    reason="Live HIBP test is disabled",
)
def test_live_hibp_detects_compromised_password():
    with httpx.Client() as client:
        result = is_password_compromised("password123", client)

    assert result is True