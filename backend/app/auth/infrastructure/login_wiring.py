from collections.abc import Callable
from uuid import UUID

from sqlalchemy.engine import Engine

from app.auth.application.login import authenticate_user

from app.auth.infrastructure.login_persistence import find_password_credential, replace_password_hash_if_unchanged
from app.auth.infrastructure.password_hash import verify_and_prepare_rehash

def make_login_handler(
        *,
        engine: Engine,
        dummy_password_hash: str
) -> Callable[[str, str], tuple[UUID, str] | None]:

    def handler(email:str, password: str) -> tuple[UUID, str] | None:

        def lookup(canonical_email: str) -> tuple[UUID, str] | None:
            with engine.connect() as connection:
                return find_password_credential(
                    connection,
                    email=canonical_email
                )

        result = authenticate_user(
            raw_email=email,
            raw_password=password,
            find_credential=lookup,
            verify_password=verify_and_prepare_rehash,
            dummy_password_hash=dummy_password_hash
        )

        if result is None:
            return None

        user_id, verified_hash, replacement_hash = result

        if replacement_hash is not None:
            with engine.begin() as connection:
                rehash_updated = replace_password_hash_if_unchanged(
                    connection,
                    user_id=user_id,
                    old_hash=verified_hash,
                    new_hash=replacement_hash
                )

            if not rehash_updated:
                return None

        expected_hash = (
            replacement_hash
            if replacement_hash is not None
            else verified_hash
        )

        return user_id, expected_hash

    return handler