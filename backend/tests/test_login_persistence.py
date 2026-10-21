import uuid

from sqlalchemy import insert

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.infrastructure.login_persistence import find_password_credential

def test_find_password_credential_found(db_connection):
    user_id = uuid.uuid4()
    email = f"login-{uuid.uuid4().hex}@example.com"
    password_hash = "test-hash"

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=user_id,
            email=email,
            password_hash=password_hash
        )
    )

    result = find_password_credential(db_connection, email=email)

    assert result == (user_id, password_hash)

def test_find_password_credential_not_found(db_connection):
    email = f"missing-{uuid.uuid4().hex}@example.com"

    result = find_password_credential(
        db_connection,
        email=email
    )

    assert result is None