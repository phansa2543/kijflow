from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import Connection, insert, select, func

from app.models.auth_session import AuthSession
from app.models.user import User

def create_auth_session(
        connection: Connection,
        *,
        user_id: UUID,
        token_digest: bytes,
        expires_at: datetime
) -> UUID:

    session_id = uuid.uuid4()

    connection.execute(
        insert(AuthSession).values(
            id=session_id,
            user_id=user_id,
            token_digest=token_digest,
            expires_at=expires_at
        )
    )

    return session_id

def find_valid_session_user_id(
    connection: Connection,
    *,
    token_digest: bytes,
) -> UUID | None:
    statement = (
        select(AuthSession.user_id)
        .join(User, User.id == AuthSession.user_id)
        .where(
            AuthSession.token_digest == token_digest,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > func.now(),
        )
    )

    return connection.execute(statement).scalar_one_or_none()