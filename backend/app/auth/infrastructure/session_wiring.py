from datetime import datetime, timedelta, timezone
from collections.abc import Callable
from uuid import UUID

from sqlalchemy.engine import Engine

from app.auth.infrastructure.login_persistence import lock_and_validate_credential
from app.auth.infrastructure.session_persistence import create_auth_session
from app.auth.infrastructure.session_token import generate_session_token, digest_session_token

def make_session_creation_handler(
        *,
        engine: Engine,
        session_lifetime: timedelta
) -> Callable[[UUID, str], str | None]:

    if session_lifetime <= timedelta(0):
        raise ValueError("session_lifetime must be positive")

    def handler(user_id: UUID, expected_hash: str) -> str | None:
        token = generate_session_token()
        token_digest = digest_session_token(token)
        expires_at = datetime.now(timezone.utc) + session_lifetime

        with engine.begin() as connection:
            credential_valid = lock_and_validate_credential(
                connection,
                user_id=user_id,
                expected_hash=expected_hash
            )

            if not credential_valid:
                return None

            create_auth_session(
                connection,
                user_id=user_id,
                token_digest=token_digest,
                expires_at=expires_at
            )

        return token

    return handler