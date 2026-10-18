import uuid
import httpx

from sqlalchemy import insert
from sqlalchemy.engine import Connection, Engine

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.email import canonicalize_email
from app.auth.screening import screen_password
from app.auth.password_hash import hash_password


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


def register_user(
    engine: Engine,
    *,
    raw_email: str,
    raw_password: str,
    common_passwords: set[str],
    client: httpx.Client,
) -> uuid.UUID:
    email = canonicalize_email(raw_email)

    password = screen_password(
        raw_password,
        common_passwords,
        client,
    )

    password_hash = hash_password(password)

    with engine.begin() as connection:
        user_id = create_user_with_credential(
            connection,
            email=email,
            password_hash=password_hash,
        )

    return user_id