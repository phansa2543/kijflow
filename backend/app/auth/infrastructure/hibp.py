import re, httpx, hashlib

from collections.abc import Callable

from app.auth.application.errors import ScreeningUnavailable

class PasswordScreeningUnavailableError(Exception):
    pass

def is_hash_suffix_compromised(suffix: str, response_text: str) -> bool:
    if not re.fullmatch(r"[0-9A-Fa-f]{35}", suffix):
        raise ValueError("Invalid HIBP input suffix")
    
    if not response_text.strip():
        raise ValueError("Empty HIBP response")
    
    compromised = False
    seen_suffixes = set()

    for line in response_text.splitlines():
        parts = line.split(":")

        if len(parts) != 2:
            raise ValueError("Invalid HIBP response format")

        returned_suffix, count = parts
        normalized_suffix = returned_suffix.upper()

        if normalized_suffix in seen_suffixes:
            raise ValueError("Duplicate HIBP response suffix")

        seen_suffixes.add(normalized_suffix)

        if not re.fullmatch(r"[0-9A-Fa-f]{35}", returned_suffix):
            raise ValueError("Invalid HIBP response suffix")

        if not re.fullmatch(r"[0-9]+", count):
            raise ValueError("Invalid HIBP response count")
        
        occurrence_count = int(count)

        if occurrence_count < 0:
            raise ValueError("Invalid HIBP response count")

        if returned_suffix.upper() == suffix.upper() and occurrence_count > 0:
            compromised = True

    return compromised

def fetch_hibp_range(prefix: str, client: httpx.Client) -> str:
    if not re.fullmatch(r"[0-9A-Fa-f]{5}", prefix):
        raise ValueError("Invalid HIBP hash prefix")

    response = client.get(
        f"https://api.pwnedpasswords.com/range/{prefix.upper()}",
        headers={"Add-Padding": "true"},
        timeout=5.0,
    )

    response.raise_for_status()
    return response.text

def is_password_compromised(password: str, client: httpx.Client) -> bool:
    prefix, suffix = get_password_hash_parts(password)

    try:
        response_text = fetch_hibp_range(prefix, client)
        return is_hash_suffix_compromised(suffix, response_text)
    except (httpx.HTTPError, ValueError):
        raise PasswordScreeningUnavailableError(
            "Password screening temporarily unavailable"
        ) from None

def get_password_sha1(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def get_password_hash_parts(password: str) -> tuple[str, str]:
    password_hash = get_password_sha1(password)

    prefix = password_hash[:5]
    suffix = password_hash[5:]

    return prefix, suffix

def make_compromised_checker(
    client: httpx.Client,
) -> Callable[[str], bool]:

    def check(password: str) -> bool:
        try:
            return is_password_compromised(password, client)
        except PasswordScreeningUnavailableError:
            pass

        raise ScreeningUnavailable(
            "Password screening temporarily unavailable"
        )

    return check