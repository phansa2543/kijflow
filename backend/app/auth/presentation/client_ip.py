from ipaddress import IPv6Address, ip_address

from fastapi import Request

from app.auth.application.errors import (
    RegistrationLimiterUnavailable,
)


def resolve_direct_client_ip(request: Request) -> str:
    if request.client is None:
        raise RegistrationLimiterUnavailable(
            "Client identity unavailable"
        )

    try:
        address = ip_address(request.client.host)
    except ValueError:
        raise RegistrationLimiterUnavailable(
            "Client identity unavailable"
        ) from None

    if isinstance(address, IPv6Address):
        if address.scope_id is not None:
            raise RegistrationLimiterUnavailable(
                "Client identity unavailable"
            )

        if address.ipv4_mapped is not None:
            return str(address.ipv4_mapped)

    return str(address)