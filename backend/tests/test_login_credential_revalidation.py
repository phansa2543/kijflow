import uuid

from sqlalchemy import insert

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.infrastructure.login_persistence import credential_matches_verified_hash

def test_credential_matches_verified_hash(db_connection):
    user_id = uuid.uuid4()
    email = f"revalidation-{uuid.uuid4().hex}@example.com"
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

    result = credential_matches_verified_hash(
        db_connection,
        user_id=user_id,
        verified_hash=stored_hash
    )

    assert result is True

def test_credential_matches_stale_hash(db_connection):
    user_id = uuid.uuid4()
    email = f"revalidation-stale-{uuid.uuid4().hex}@example.com"
    stored_hash = "current-hash"
    verified_hash = "old-hash"

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

    result = credential_matches_verified_hash(
        db_connection,
        user_id=user_id,
        verified_hash=verified_hash
    )

    assert result is False

def test_credential_matches_unknown_user(db_connection):
    user_id = uuid.uuid4()
    verified_hash = "some-hash"

    result = credential_matches_verified_hash(
        db_connection,
        user_id=user_id,
        verified_hash=verified_hash
    )

    assert result is False