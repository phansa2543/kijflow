import uuid

from sqlalchemy import insert
from sqlalchemy.engine import Connection, Engine

from app.models.user import User
from app.models.password_credential import UserPasswordCredential


def create_user_with_credential(
    connection: Connection,
    *,
    email: str,
    password_hash: str,
) -> uuid.UUID:
    user_id = uuid.uuid4()

    connection.execute(
        insert(User).values(id=user_id)
    )

    connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
        )
    )

    return user_id

def persist_new_user_with_credential(
    engine: Engine,
    *,
    email: str,
    password_hash: str,
) -> uuid.UUID:
    with engine.begin() as connection:
        return create_user_with_credential(
            connection,
            email=email,
            password_hash=password_hash,
        )