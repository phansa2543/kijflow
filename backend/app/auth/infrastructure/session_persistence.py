from datetime import datetime
from uuid import UUID
import uuid

from sqlalchemy import Connection, insert

from app.models.auth_session import AuthSession

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