from collections.abc import Callable
from uuid import UUID

from app.auth.domain.email import canonicalize_email
from app.auth.domain.password import normalize_password

def authenticate_user(
        *,
        raw_email: str,
        raw_password: str,
        find_credential: Callable[[str], tuple[UUID, str] | None],
        verify_password: Callable[[str, str], tuple[bool, str | None]],
        dummy_password_hash: str
) -> tuple[UUID, str, str | None] | None:

    email = canonicalize_email(raw_email)
    password = normalize_password(raw_password)
    credential = find_credential(email)

    if credential is None:
        hash_to_verify = dummy_password_hash
    else:
        hash_to_verify = credential[1]

    verified, replacement_hash = verify_password(password, hash_to_verify)

    if credential is None or not verified:
        return None

    return credential[0], credential[1], replacement_hash