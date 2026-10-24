import hashlib, secrets, re

_SESSION_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{43}")

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def digest_session_token(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()

def validate_session_token(token: object) -> str | None:
    if not isinstance(token, str):
        return None

    if _SESSION_TOKEN_PATTERN.fullmatch(token) is None:
        return None

    return token