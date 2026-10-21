import uuid

from sqlalchemy import insert, select

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.infrastructure.login_persistence import replace_password_hash_if_unchanged

def test_replace_password_hash_success(db_connection):
    user_id = uuid.uuid4()
    email = f"rehash-{uuid.uuid4().hex}@example.com"
    old_hash = "old-hash"
    new_hash = "new-hash"

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email=email,
            password_hash=old_hash
        )
    )

    result = replace_password_hash_if_unchanged(
        db_connection, 
        user_id=user_id, 
        old_hash=old_hash, 
        new_hash=new_hash
    )

    assert result is True

    stored_hash = db_connection.execute(
        select(UserPasswordCredential.password_hash).where(
            UserPasswordCredential.user_id == user_id
        )
    ).scalar_one()

    assert stored_hash == new_hash

def test_replace_password_hash_stale(db_connection):
    user_id = uuid.uuid4()
    email = f"rehash-stale-{uuid.uuid4().hex}@example.com"
    stored_hash = "current-hash"
    old_hash = "outdated-hash"
    new_hash = "new-hash"

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email=email,
            password_hash=stored_hash
        )
    )

    result = replace_password_hash_if_unchanged(
        db_connection,
        user_id=user_id,
        old_hash=old_hash,
        new_hash=new_hash
    )

    assert result is False

    actual_hash = db_connection.execute(
        select(UserPasswordCredential.password_hash).where(
            UserPasswordCredential.user_id == user_id
        )
    ).scalar_one()

    assert actual_hash == stored_hash

def test_replace_password_hash_unknown_user(db_connection):
    user_id = uuid.uuid4()
    old_hash = "old-hash"
    new_hash = "new-hash"

    result = replace_password_hash_if_unchanged(
        db_connection,
        user_id=user_id,
        old_hash=old_hash,
        new_hash=new_hash
    )

    assert result is False

    credentail = db_connection.execute(
        select(UserPasswordCredential.user_id).where(
            UserPasswordCredential.user_id == user_id
        )
    ).scalar_one_or_none()

    assert credentail is None