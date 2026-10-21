from uuid import UUID

from sqlalchemy import Connection, select, update, func

from app.models.password_credential import UserPasswordCredential

def find_password_credential(
        connection: Connection,
        *,
        email: str
) -> tuple[UUID, str] | None:
    
    row = connection.execute(
        select(
            UserPasswordCredential.user_id,
            UserPasswordCredential.password_hash
        ).where(
            UserPasswordCredential.email == email
        )
    ).one_or_none()

    if row is None:
        return None

    return row.user_id, row.password_hash

def replace_password_hash_if_unchanged(
        connection: Connection,
        *,
        user_id: UUID,
        old_hash: str,
        new_hash: str
) -> bool:
    result = connection.execute(
        update(UserPasswordCredential).where(
            UserPasswordCredential.user_id == user_id,
            UserPasswordCredential.password_hash == old_hash
        ).values(
            password_hash=new_hash,
            updated_at=func.now()
        )
    )

    return result.rowcount == 1

def credential_matches_verified_hash(
        connection: Connection,
        *,
        user_id: UUID,
        verified_hash: str
) -> bool:

    result = connection.execute(
        select(UserPasswordCredential.user_id).where(
            UserPasswordCredential.user_id == user_id,
            UserPasswordCredential.password_hash == verified_hash
        )
    ).scalar_one_or_none()

    return result is not None

def lock_and_validate_credential(
        connection: Connection,
        *,
        user_id: UUID,
        expected_hash: str
) -> bool:

    stored_hash = connection.execute(
        select(UserPasswordCredential.password_hash).where(
            UserPasswordCredential.user_id == user_id
        ).with_for_update()
    ).scalar_one_or_none()

    return (stored_hash is not None) and (stored_hash == expected_hash)