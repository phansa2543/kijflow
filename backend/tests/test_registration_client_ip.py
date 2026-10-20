import pytest

from fastapi import Request

from app.auth.application.errors import (
    RegistrationLimiterUnavailable,
)
from app.auth.presentation.client_ip import (
    resolve_direct_client_ip,
)


def make_request(
    client_host: str | None,
    headers=None,
) -> Request:
    return Request({
        "type": "http",
        "client": (
            (client_host, 12345)
            if client_host is not None
            else None
        ),
        "headers": headers or [],
    })


@pytest.mark.parametrize(
    "raw_ip, expected",
    [
        ("192.0.2.10", "192.0.2.10"),
        ("2001:0db8::1", "2001:db8::1"),
        ("::ffff:192.0.2.10", "192.0.2.10"),
    ],
)
def test_client_ip_normalization(raw_ip, expected):
    request = make_request(raw_ip)

    assert resolve_direct_client_ip(request) == expected


@pytest.mark.parametrize(
    "invalid_ip",
    [
        None,
        "not-an-ip",
        "fe80::1%eth0",
    ],
)
def test_invalid_client_ip_fails_closed(invalid_ip):
    request = make_request(invalid_ip)

    with pytest.raises(RegistrationLimiterUnavailable):
        resolve_direct_client_ip(request)


def test_forwarded_headers_are_not_trusted_directly():
    request = make_request(
        "192.0.2.10",
        headers=[
            (b"x-forwarded-for", b"203.0.113.99"),
            (b"x-real-ip", b"203.0.113.88"),
            (b"forwarded", b"for=203.0.113.77"),
        ],
    )

    assert resolve_direct_client_ip(request) == "192.0.2.10"