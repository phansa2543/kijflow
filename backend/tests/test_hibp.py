import pytest, httpx

from app.auth.password import get_password_sha1
from app.auth.hibp import (
    is_hash_suffix_compromised, 
    fetch_hibp_range, 
    is_password_compromised, 
    PasswordScreeningUnavailableError
)

def test_is_hash_suffix_compromised_returns_true():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:15234"

    result = is_hash_suffix_compromised(suffix, response_text)

    assert result is True

def test_is_hash_suffix_compromised_returns_false_when_not_found():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:100"

    result = is_hash_suffix_compromised(suffix, response_text)

    assert result is False

def test_is_hash_suffix_compromised_ignores_padding():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:0"

    result = is_hash_suffix_compromised(suffix, response_text)

    assert result is False

def test_is_hash_suffix_compromised_rejects_malformed_response():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = "INVALID_RESPONSE"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_invalid_count():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:INVALID"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_negative_count():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:-1"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_invalid_suffix():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = "NOT_A_VALID_SUFFIX:100"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_empty_response():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = ""

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_signed_count():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:+100"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_invalid_input_suffix():
    suffix = "INVALID_SUFFIX"
    response_text = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:100"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_duplicate_suffix():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:100\n{suffix}:0"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_blank_line():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:100\n\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:0"

    with pytest.raises(ValueError):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_rejects_extra_separator():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    response_text = f"{suffix}:100:INVALID"

    with pytest.raises(ValueError, match="Invalid HIBP response format"):
        is_hash_suffix_compromised(suffix, response_text)

def test_is_hash_suffix_compromised_error_does_not_leak_response():
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"
    sensitive_marker = "SENSITIVE_TEST_MARKER"
    response_text = f"{suffix}:100:{sensitive_marker}"

    with pytest.raises(ValueError) as exc_info:
        is_hash_suffix_compromised(suffix, response_text)

    assert sensitive_marker not in str(exc_info.value)
    assert suffix not in str(exc_info.value)

def test_fetch_hibp_range_sends_correct_request():
    prefix = "CBFDA"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == (
            "https://api.pwnedpasswords.com/range/CBFDA"
        )
        assert request.headers["Add-Padding"] == "true"

        return httpx.Response(
            200,
            text="C6008F9CAB4083784CBD1874F76618D2A97:100",
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        result = fetch_hibp_range(prefix, client)

    assert result == "C6008F9CAB4083784CBD1874F76618D2A97:100"

def test_fetch_hibp_range_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Simulated timeout")

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        with pytest.raises(httpx.ReadTimeout):
            fetch_hibp_range("CBFDA", client)

def test_fetch_hibp_range_server_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable")

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            fetch_hibp_range("CBFDA", client)

def test_fetch_hibp_range_connection_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Simulated connection failure")

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        with pytest.raises(httpx.ConnectError):
            fetch_hibp_range("CBFDA", client)

def test_fetch_hibp_range_rejects_invalid_prefix():
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail("HTTP request must not be sent")

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        with pytest.raises(ValueError, match="Invalid HIBP hash prefix"):
            fetch_hibp_range("INVALID", client)

def test_is_password_compromised_returns_true():
    password = "password123"
    suffix = "C6008F9CAB4083784CBD1874F76618D2A97"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/range/CBFDA"
        assert request.headers["Add-Padding"] == "true"

        return httpx.Response(200, text=f"{suffix}:100")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = is_password_compromised(password, client)

    assert result is True

def test_is_password_compromised_returns_false():
    password = "password123"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/range/CBFDA"

        return httpx.Response(
            200,
            text="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA:100",
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = is_password_compromised(password, client)

    assert result is False

def test_is_password_compromised_fails_closed_on_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Simulated timeout")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(
            PasswordScreeningUnavailableError,
            match="Password screening temporarily unavailable",
        ):
            is_password_compromised("password123", client)

def test_is_password_compromised_fails_closed_on_malformed_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="INVALID_RESPONSE")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(
            PasswordScreeningUnavailableError,
            match="Password screening temporarily unavailable"
        ):
            is_password_compromised("password123", client)

def test_is_password_compromised_fails_closed_on_server_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(
            PasswordScreeningUnavailableError,
            match="Password screening temporarily unavailable"
        ):
            is_password_compromised("password123", client)

def test_is_password_compromised_error_does_not_leak_secrets():
    password = "password123"
    sensitive_marker = "SENSITIVE_TEST_MARKER"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=f"{sensitive_marker}:INVALID",
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(PasswordScreeningUnavailableError) as exc_info:
            is_password_compromised(password, client)

    error_message = str(exc_info.value)

    assert error_message == "Password screening temporarily unavailable"
    assert password not in error_message
    assert sensitive_marker not in error_message
    assert get_password_sha1(password) not in error_message

def test_is_password_compromised_fails_closed_on_connection_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Simulated connection failure")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(
            PasswordScreeningUnavailableError,
            match="Password screening temporarily unavailable",
        ):
            is_password_compromised("password123", client)