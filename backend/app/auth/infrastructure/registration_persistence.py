import uuid

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Connection, Engine

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.application.errors import RegistrationConflict

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
    try:
        with engine.begin() as connection:
            return create_user_with_credential(
                connection,
                email=email,
                password_hash=password_hash,
            )
    except IntegrityError as exc:
        if _is_email_unique_violation(exc):
            raise RegistrationConflict(
                "Registration could not be completed"
            ) from None
        raise

def _is_email_unique_violation(exc: IntegrityError) -> bool:
    original = exc.orig

    return (
        getattr(original, "sqlstate", None) == "23505"
        and getattr(
            getattr(original, "diag", None),
            "constraint_name",
            None,
        ) == "uq_user_password_credentials_email"
    )