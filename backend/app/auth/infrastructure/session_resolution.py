from uuid import UUID

from sqlalchemy import Connection

from app.auth.infrastructure.session_token import (
    validate_session_token,
    digest_session_token,
)
from app.auth.infrastructure.session_persistence import (
    find_valid_session_user_id,
    revoke_current_session
)


def resolve_session_user_id(
    connection: Connection,
    *,
    raw_token: object,
) -> UUID | None:
    token = validate_session_token(raw_token)

    if token is None:
        return None

    token_digest = digest_session_token(token)

    return find_valid_session_user_id(
        connection,
        token_digest=token_digest,
    )

def revoke_session_by_raw_token(
    connection: Connection,
    *,
    raw_token: object,
) -> bool:
    token = validate_session_token(raw_token)

    if token is None:
        return False

    return revoke_current_session(
        connection,
        token_digest=digest_session_token(token),
    )