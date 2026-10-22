import hashlib, os, hmac

def make_account_counter_identifier(
    canonical_email: str,
    secret: bytes,
) -> str:
    if not canonical_email:
        raise ValueError("canonical_email must not be empty")

    if len(secret) < 32:
        raise ValueError("login counter HMAC secret is too short")

    return hmac.new(
        secret,
        canonical_email.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def load_login_counter_hmac_secret() -> bytes:
    value = os.environ.get("LOGIN_COUNTER_HMAC_SECRET")

    if value is None or len(value) != 64:
        raise ValueError("invalid login counter HMAC configuration")

    try:
        secret = bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(
            "invalid login counter HMAC configuration"
        ) from exc

    if len(secret) != 32:
        raise ValueError("invalid login counter HMAC configuration")

    return secret