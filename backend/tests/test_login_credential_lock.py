import uuid

from sqlalchemy import insert

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.infrastructure.login_persistence import lock_and_validate_credential

def test_lock_and_validate_credential_match(db_connection):
    user_id = uuid.uuid4()
    email = f"credential-lock-{uuid.uuid4().hex}@example.com"
    stored_hash = "stored-hash"

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

    result = lock_and_validate_credential(
        db_connection,
        user_id=user_id,
        expected_hash=stored_hash
    )

    assert result is True

def test_lock_and_validate_credential_stale_hash(db_connection):
    user_id = uuid.uuid4()
    email = f"credential-lock-stale-{uuid.uuid4().hex}@example.com"
    stored_hash = "current-hash"
    expected_hash = "old-hash"

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

    result = lock_and_validate_credential(
        db_connection,
        user_id=user_id,
        expected_hash=expected_hash
    )

    assert result is False

def test_lock_and_validate_credential_unknown_user(db_connection):
    user_id = uuid.uuid4()
    expected_hash = "some-hash"

    result = lock_and_validate_credential(
        db_connection,
        user_id=user_id,
        expected_hash=expected_hash
    )

    assert result is False