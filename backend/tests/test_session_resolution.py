
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import insert, update

from app.auth.infrastructure.session_resolution import (
    resolve_session_user_id,
    revoke_session_by_raw_token
)
from app.auth.infrastructure.session_token import (
    digest_session_token,
    generate_session_token,
)
from app.models.auth_session import AuthSession
from app.models.user import User


def create_session(connection, user_id):
    token = generate_session_token()

    connection.execute(
        insert(AuthSession).values(
            id=uuid.uuid4(),
            user_id=user_id,
            token_digest=digest_session_token(token),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )

    return token


def test_valid_raw_token_resolves_user(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    token = create_session(db_connection, user_id)

    assert resolve_session_user_id(
        db_connection,
        raw_token=token,
    ) == user_id


@pytest.mark.parametrize(
    "raw_token",
    [None, "", "short", "a" * 44, 123, "ก" * 43],
)
def test_missing_or_malformed_token_denied(db_connection, raw_token):
    assert resolve_session_user_id(
        db_connection,
        raw_token=raw_token,
    ) is None


def test_unknown_token_denied(db_connection):
    assert resolve_session_user_id(
        db_connection,
        raw_token=generate_session_token(),
    ) is None


def test_expired_token_denied(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    token = create_session(db_connection, user_id)
    now = datetime.now(timezone.utc)

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == digest_session_token(token))
        .values(
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
    )

    assert resolve_session_user_id(
        db_connection,
        raw_token=token,
    ) is None


def test_revoked_token_denied(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    token = create_session(db_connection, user_id)

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == digest_session_token(token))
        .values(revoked_at=datetime.now(timezone.utc))
    )

    assert resolve_session_user_id(
        db_connection,
        raw_token=token,
    ) is None


def test_multiple_sessions_are_independent(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    first_token = create_session(db_connection, user_id)
    second_token = create_session(db_connection, user_id)

    db_connection.execute(
        update(AuthSession)
        .where(AuthSession.token_digest == digest_session_token(first_token))
        .values(revoked_at=datetime.now(timezone.utc))
    )

    assert resolve_session_user_id(
        db_connection,
        raw_token=first_token,
    ) is None

    assert resolve_session_user_id(
        db_connection,
        raw_token=second_token,
    ) == user_id

def test_revoke_valid_raw_token(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(insert(User).values(id=user_id))
    token = create_session(db_connection, user_id)

    assert revoke_session_by_raw_token(
        db_connection,
        raw_token=token,
    ) is True

    assert resolve_session_user_id(
        db_connection,
        raw_token=token,
    ) is None

    assert revoke_session_by_raw_token(
        db_connection,
        raw_token=token,
    ) is False


@pytest.mark.parametrize(
    "token",
    [None, "", "short", "a" * 44, 123],
)
def test_revoke_invalid_raw_token(db_connection, token):
    assert revoke_session_by_raw_token(
        db_connection,
        raw_token=token,
    ) is False


def test_revoke_one_of_multiple_sessions(db_connection):
    user_id = uuid.uuid4()

    db_connection.execute(insert(User).values(id=user_id))

    first_token = create_session(db_connection, user_id)
    second_token = create_session(db_connection, user_id)

    assert revoke_session_by_raw_token(
        db_connection,
        raw_token=first_token,
    ) is True

    assert resolve_session_user_id(
        db_connection,
        raw_token=first_token,
    ) is None

    assert resolve_session_user_id(
        db_connection,
        raw_token=second_token,
    ) == user_id