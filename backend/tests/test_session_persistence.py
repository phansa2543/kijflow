
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete, insert, update, func
from sqlalchemy.exc import IntegrityError

from app.auth.infrastructure.session_persistence import (
    find_valid_session_user_id,
    revoke_current_session
)
from app.auth.infrastructure.session_token import (
    digest_session_token,
    generate_session_token,
)
from app.models.auth_session import AuthSession
from app.models.user import User


def create_user(connection):
    user_id = uuid.uuid4()

    connection.execute(
        insert(User).values(id=user_id)
    )

    return user_id


def create_session(
    connection,
    user_id,
    *,
    expires_in=timedelta(hours=1),
    revoked=False,
):
    now = datetime.now(timezone.utc)
    token = generate_session_token()
    digest = digest_session_token(token)

    connection.execute(
        insert(AuthSession).values(
            id=uuid.uuid4(),
            user_id=user_id,
            token_digest=digest,
            expires_at=now + expires_in,
            revoked_at=None,
        )
    )

    if revoked:
        connection.execute(
            update(AuthSession)
            .where(AuthSession.token_digest == digest)
            .values(revoked_at=func.now())
    )

    return digest


def test_valid_session_returns_user_id(db_connection):
    user_id = create_user(db_connection)
    digest = create_session(db_connection, user_id)

    result = find_valid_session_user_id(
        db_connection,
        token_digest=digest,
    )

    assert result == user_id


def test_expired_session_is_denied(db_connection):
    user_id = create_user(db_connection)

    digest = create_session(
        db_connection,
        user_id,
    )

    now = datetime.now(timezone.utc)

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == digest)
        .values(
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
    )

    result = find_valid_session_user_id(
        db_connection,
        token_digest=digest,
    )

    assert result is None

def test_revoked_session_is_denied(db_connection):
    user_id = create_user(db_connection)

    digest = create_session(
        db_connection,
        user_id,
        revoked=True,
    )

    result = find_valid_session_user_id(
        db_connection,
        token_digest=digest,
    )

    assert result is None


def test_unknown_digest_is_denied(db_connection):
    unknown_digest = digest_session_token(
        generate_session_token()
    )

    result = find_valid_session_user_id(
        db_connection,
        token_digest=unknown_digest,
    )

    assert result is None


def test_referenced_user_cannot_be_deleted(
    db_connection,
):
    user_id = create_user(db_connection)
    digest = create_session(db_connection, user_id)

    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            db_connection.execute(
                delete(User).where(User.id == user_id)
            )

    result = find_valid_session_user_id(
        db_connection,
        token_digest=digest,
    )

    assert result == user_id


def test_multiple_sessions_are_independent(
    db_connection,
):
    user_id = create_user(db_connection)

    first_digest = create_session(
        db_connection,
        user_id,
    )

    second_digest = create_session(
        db_connection,
        user_id,
    )

    assert first_digest != second_digest

    assert find_valid_session_user_id(
        db_connection,
        token_digest=first_digest,
    ) == user_id

    assert find_valid_session_user_id(
        db_connection,
        token_digest=second_digest,
    ) == user_id

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == first_digest)
        .values(revoked_at=datetime.now(timezone.utc))
    )

    assert find_valid_session_user_id(
        db_connection,
        token_digest=first_digest,
    ) is None

    assert find_valid_session_user_id(
        db_connection,
        token_digest=second_digest,
    ) == user_id

def test_revoke_current_session(db_connection):
    user_id = create_user(db_connection)
    digest = create_session(db_connection, user_id)

    assert revoke_current_session(
        db_connection,
        token_digest=digest,
    ) is True

    assert find_valid_session_user_id(
        db_connection,
        token_digest=digest,
    ) is None

    # Revocation must be idempotent at the persistence level.
    assert revoke_current_session(
        db_connection,
        token_digest=digest,
    ) is False


def test_revoke_unknown_or_expired_session(db_connection):
    unknown_digest = digest_session_token(
        generate_session_token()
    )

    assert revoke_current_session(
        db_connection,
        token_digest=unknown_digest,
    ) is False

    user_id = create_user(db_connection)
    expired_digest = create_session(db_connection, user_id)

    now = datetime.now(timezone.utc)

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == expired_digest)
        .values(
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
    )

    assert revoke_current_session(
        db_connection,
        token_digest=expired_digest,
    ) is False


def test_revoke_only_current_session(db_connection):
    user_id = create_user(db_connection)

    first_digest = create_session(db_connection, user_id)
    second_digest = create_session(db_connection, user_id)

    assert revoke_current_session(
        db_connection,
        token_digest=first_digest,
    ) is True

    assert find_valid_session_user_id(
        db_connection,
        token_digest=first_digest,
    ) is None

    assert find_valid_session_user_id(
        db_connection,
        token_digest=second_digest,
    ) == user_id