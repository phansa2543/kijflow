import uuid

from collections.abc import Callable

from app.auth.domain.email import canonicalize_email

def register_user(
    *,
    raw_email: str,
    raw_password: str,
    screen: Callable[[str], str],
    hash_password: Callable[[str], str],
    persist: Callable[[str, str], uuid.UUID]
) -> uuid.UUID:
    email = canonicalize_email(raw_email)

    password = screen(raw_password)

    password_hash = hash_password(password)

    return persist(email, password_hash)