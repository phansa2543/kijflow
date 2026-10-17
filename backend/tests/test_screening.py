import pytest

from unittest.mock import Mock

from app.auth.screening import screen_password

def test_common_password_rejected_without_hibp_call():
    client = Mock()
    common_passwords = {"password123"}

    with pytest.raises(ValueError, match="Password is not allowed"):
        screen_password("password123", common_passwords, client)

    client.get.assert_not_called()

def test_hibp_compromised_password_rejected():
    client = Mock()
    common_passwords = set()
    password = "password123"

    # จำลอง HIBP ส่งข้อมูลว่ารหัสผ่านนี้เคยรั่วไหล
    from app.auth.password import get_password_hash_parts

    _, suffix = get_password_hash_parts(password)
    client.get.return_value.text = f"{suffix}:10"
    client.get.return_value.raise_for_status.return_value = None

    with pytest.raises(ValueError, match="Password is not allowed"):
        screen_password(password, common_passwords, client)

    client.get.assert_called_once()

def test_clean_password_returns_normalized_password():
    client = Mock()
    common_passwords = set()

    raw_password = "Cafe\u0301Secure123"
    expected_password = "CaféSecure123"

    client.get.return_value.text = "A" * 35 + ":0"
    client.get.return_value.raise_for_status.return_value = None

    result = screen_password(raw_password, common_passwords, client)

    assert result == expected_password
    client.get.assert_called_once()

import httpx

from app.auth.hibp import PasswordScreeningUnavailableError


def test_hibp_timeout_fails_closed():
    client = Mock()
    client.get.side_effect = httpx.ReadTimeout("Request timed out")
    common_passwords = set()

    with pytest.raises(
        PasswordScreeningUnavailableError,
        match="Password screening temporarily unavailable",
    ):
        screen_password("SafeExample123", common_passwords, client)

    client.get.assert_called_once()

def test_hibp_malformed_response_fails_closed():
    client = Mock()
    client.get.return_value.text = "INVALID_RESPONSE"
    client.get.return_value.raise_for_status.return_value = None

    with pytest.raises(
        PasswordScreeningUnavailableError,
        match="Password screening temporarily unavailable",
    ):
        screen_password("SafeExample123", set(), client)

    client.get.assert_called_once()

from app.auth.password import get_password_hash_parts


def test_hibp_zero_count_padding_allows_password():
    client = Mock()
    password = "SafeExample123"

    _, suffix = get_password_hash_parts(password)

    client.get.return_value.text = f"{suffix}:0"
    client.get.return_value.raise_for_status.return_value = None

    result = screen_password(password, set(), client)

    assert result == password
    client.get.assert_called_once()

def test_short_password_rejected_without_hibp_call():
    client = Mock()

    with pytest.raises(ValueError, match="Password is too short"):
        screen_password("1234567", set(), client)

    client.get.assert_not_called()

def test_long_password_rejected_without_hibp_call():
    client = Mock()

    with pytest.raises(ValueError, match="Password is too long"):
        screen_password("A" * 129, set(), client)

    client.get.assert_not_called()

def test_nfc_normalization_before_local_blocklist():
    client = Mock()

    raw_password = "Cafe\u0301Secure123"
    common_passwords = {"CaféSecure123"}

    with pytest.raises(ValueError, match="Password is not allowed"):
        screen_password(raw_password, common_passwords, client)

    client.get.assert_not_called()

def test_local_blocklist_preserves_case_and_whitespace():
    client = Mock()
    common_passwords = {"SecurePassword123"}

    password = " SecurePassword123"

    client.get.return_value.text = "A" * 35 + ":0"
    client.get.return_value.raise_for_status.return_value = None

    result = screen_password(password, common_passwords, client)

    assert result == password
    client.get.assert_called_once()

def test_local_blocklist_preserves_case_sensitivity():
    client = Mock()
    common_passwords = {"SecurePassword123"}

    password = "securepassword123"

    client.get.return_value.text = "A" * 35 + ":0"
    client.get.return_value.raise_for_status.return_value = None

    result = screen_password(password, common_passwords, client)

    assert result == password
    client.get.assert_called_once()

def test_hibp_http_error_fails_closed():
    client = Mock()
    request = httpx.Request(
        "GET",
        "https://api.pwnedpasswords.com/range/ABCDE",
    )
    response = httpx.Response(503, request=request)

    client.get.return_value.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "Service unavailable",
            request=request,
            response=response,
        )
    )

    with pytest.raises(
        PasswordScreeningUnavailableError,
        match="Password screening temporarily unavailable",
    ):
        screen_password("SafeExample123", set(), client)

    client.get.assert_called_once()

def test_hibp_request_sends_only_hash_prefix():
    client = Mock()
    password = "SafeExample123"

    prefix, _ = get_password_hash_parts(password)
    client.get.return_value.text = "A" * 35 + ":0"

    assert screen_password(password, set(), client) == password

    client.get.assert_called_once_with(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        headers={"Add-Padding": "true"},
        timeout=5.0,
    )

def test_hibp_failure_does_not_leak_password():
    client = Mock()
    password = "UniqueSecretExample123"

    client.get.side_effect = httpx.ConnectError(
        f"Connection failed while checking {password}"
    )

    with pytest.raises(PasswordScreeningUnavailableError) as exc_info:
        screen_password(password, set(), client)

    assert str(exc_info.value) == (
        "Password screening temporarily unavailable"
    )
    assert password not in str(exc_info.value)
    assert exc_info.value.__cause__ is None

def test_hibp_failure_has_suppressed_exception_context():
    client = Mock()
    password = "UniqueSecretExample123"

    client.get.side_effect = httpx.ConnectError(
        f"Connection failed while checking {password}"
    )

    with pytest.raises(PasswordScreeningUnavailableError) as exc_info:
        screen_password(password, set(), client)

    error = exc_info.value

    assert error.__suppress_context__ is True
    assert error.__cause__ is None
    assert error.__context__ is not None

import traceback


def test_hibp_failure_standard_traceback_does_not_leak_password():
    client = Mock()
    password = "UniqueSecretExample123"

    client.get.side_effect = httpx.ConnectError(
        f"Connection failed while checking {password}"
    )

    with pytest.raises(PasswordScreeningUnavailableError) as exc_info:
        screen_password(password, set(), client)

    formatted_traceback = "".join(
        traceback.format_exception(exc_info.value)
    )

    assert password not in formatted_traceback
    assert "Connection failed while checking" not in formatted_traceback

def test_hibp_connection_error_fails_closed():
    client = Mock()
    client.get.side_effect = httpx.ConnectError("Connection failed")

    with pytest.raises(
        PasswordScreeningUnavailableError,
        match="Password screening temporarily unavailable",
    ):
        screen_password("SafeExample123", set(), client)

    client.get.assert_called_once()