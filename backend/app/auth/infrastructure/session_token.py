import hashlib, secrets

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def digest_session_token(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()