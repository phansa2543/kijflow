import uuid, pytest

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

def test_allows_password_credential_for_existing_user(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email="alice@example.com",
            password_hash="test-argon2-hash"
        )
    )

    credential = db_connection.execute(
        select(
            UserPasswordCredential.user_id,
            UserPasswordCredential.email,
            UserPasswordCredential.password_hash,
            ).where(
            UserPasswordCredential.user_id == user_id
        )
    ).one()

    assert credential.user_id == user_id
    assert credential.email == "alice@example.com"
    assert credential.password_hash == "test-argon2-hash"

def test_rejects_second_password_credential_for_same_user(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email="alice@example.com",
            password_hash="test-argon2-hash"
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email="bob@example.com",
                password_hash="test-argon2-hash-2"
            )
        )

def test_rejects_duplicate_credential_email_across_user(db_connection):
    first_user_id = uuid.uuid4()
    second_user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=first_user_id
        )
    )

    db_connection.execute(
        insert(User).values(
            id=second_user_id
        )
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=first_user_id,
            email="alice@example.com",
            password_hash="test-argon2-hash"
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(UserPasswordCredential).values(
                user_id=second_user_id,
                email="alice@example.com",
                password_hash="test-argon2-hash-2"
            )
        )

def test_rejects_password_credential_for_nonexistent_user(db_connection):
    user_id = uuid.uuid4()

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email="alice@example.com",
                password_hash="test-argon2-hash"
            )
        )

def test_rejects_deleting_user_with_password_credential(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email="alice@example.com",
            password_hash="test-argon2-hash"
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            delete(User).where(
                User.id == user_id
            )
        )