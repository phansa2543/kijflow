import hashlib, uuid, pytest

from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.auth_session import AuthSession

def test_allows_auth_session_for_existing_user(db_connection):
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)

    token_digest = hashlib.sha256(b"test-session-token").digest()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=session_id,
            user_id=user_id,
            token_digest=token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None,
        )
    )

    session = db_connection.execute(
        select(
            AuthSession.id,
            AuthSession.user_id,
            AuthSession.token_digest,
            AuthSession.created_at,
            AuthSession.expires_at,
            AuthSession.revoked_at
        ).where(
            AuthSession.id == session_id
        )
    ).one()

    assert session.id == session_id
    assert session.user_id == user_id
    assert session.token_digest == token_digest
    assert session.expires_at == expires_at
    assert session.revoked_at is None

def test_rejects_auth_session_for_nonexistent_user(db_connection):
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)
    token_digest = hashlib.sha256(b"test-session-token").digest()

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(AuthSession).values(
                id=session_id,
                user_id=user_id,
                token_digest=token_digest,
                created_at=created_at,
                expires_at=expires_at,
                revoked_at=None
            )
        )

def test_rejects_duplicate_auth_session_token_digest(db_connection):
    user_id = uuid.uuid4()
    first_session_id = uuid.uuid4()
    second_session_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)
    token_digest = hashlib.sha256(b"test-session-digest").digest()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=first_session_id,
            user_id=user_id,
            token_digest=token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(AuthSession).values(
                id=second_session_id,
                user_id=user_id,
                token_digest=token_digest,
                created_at=created_at,
                expires_at=expires_at,
                revoked_at=None
            )
        )

def test_rejects_auth_session_when_expires_at_equals_created_at(db_connection):
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at
    token_digest = hashlib.sha256(b"test-session-digest").digest()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(AuthSession).values(
                id=session_id,
                user_id=user_id,
                token_digest=token_digest,
                created_at=created_at,
                expires_at=expires_at,
                revoked_at=None
            )
    )

def test_rejects_auth_session_when_revoked_at_before_created_at(db_connection):
    user_id = uuid.uuid4()

    session_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)
    revoked_at = created_at - timedelta(seconds=1)
    token_digest = hashlib.sha256(b"test-session-digest").digest()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            insert(AuthSession).values(
                id=session_id,
                user_id=user_id,
                token_digest=token_digest,
                created_at=created_at,
                expires_at=expires_at,
                revoked_at=revoked_at
            )
    )

def test_allows_auth_session_revoked_at_or_after_created_at(db_connection):
    user_id = uuid.uuid4()

    session_id = uuid.uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)
    revoked_at = created_at + timedelta(seconds=1)
    token_digest = hashlib.sha256(b"test-session-digest").digest()

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=session_id,
            user_id=user_id,
            token_digest=token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=revoked_at
        )
    )

    session = db_connection.execute(
        select(
            AuthSession.id,
            AuthSession.user_id,
            AuthSession.token_digest,
            AuthSession.created_at,
            AuthSession.expires_at,
            AuthSession.revoked_at
        ).where(
            AuthSession.id == session_id
        )
    ).one()

    assert session.revoked_at == revoked_at

def test_allows_multiple_auth_sessions_for_same_user(db_connection):
    user_id = uuid.uuid4()

    first_session_id = uuid.uuid4()
    second_session_id = uuid.uuid4()

    first_token_digest = hashlib.sha256(b"first-session-token").digest()
    second_token_digest = hashlib.sha256(b"second-session-token").digest()

    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=first_session_id,
            user_id=user_id,
            token_digest=first_token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=second_session_id,
            user_id=user_id,
            token_digest=second_token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None
        )
    )

    sessions = db_connection.execute(
        select(
            AuthSession.id,
            AuthSession.user_id,
            AuthSession.token_digest,
            AuthSession.created_at,
            AuthSession.expires_at,
            AuthSession.revoked_at
        ).where(
            AuthSession.user_id == user_id
        )
    ).all()

    assert len(sessions) == 2
    session_ids = {session.id for session in sessions}

    assert session_ids == {
        first_session_id,
        second_session_id
    }

def test_rejects_deleting_user_with_auth_session(db_connection):
    user_id = uuid.uuid4()

    session_id = uuid.uuid4()
    token_digest = hashlib.sha256(b"test-session-digest").digest()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=24)

    db_connection.execute(
        insert(User).values(
            id=user_id
        )
    )

    db_connection.execute(
        insert(AuthSession).values(
            id=session_id,
            user_id=user_id,
            token_digest=token_digest,
            created_at=created_at,
            expires_at=expires_at,
            revoked_at=None
        )
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            delete(User).where(
                User.id == user_id
            )
        )