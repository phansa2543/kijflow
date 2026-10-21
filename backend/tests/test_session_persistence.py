import uuid 
from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select

from app.models.user import User
from app.models.auth_session import AuthSession

from app.auth.infrastructure.session_persistence import create_auth_session
from app.auth.infrastructure.session_token import generate_session_token, digest_session_token

def test_create_auth_session(db_connection):
    user_id = uuid.uuid4()
    token = generate_session_token()
    token_digest = digest_session_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    session_id = create_auth_session(
        db_connection,
        user_id=user_id,
        token_digest=token_digest,
        expires_at=expires_at
    )

    result = db_connection.execute(
        select(
            AuthSession.id,
            AuthSession.user_id,
            AuthSession.token_digest,
            AuthSession.expires_at,
            AuthSession.revoked_at
        ).where(
            AuthSession.user_id == user_id
        )
    ).one()

    assert result.id == session_id
    assert result.user_id == user_id
    assert result.token_digest == token_digest
    assert result.expires_at == expires_at
    assert result.revoked_at is None

def test_create_auth_session_rollback(db_connection):
    user_id = uuid.uuid4()
    token = generate_session_token()
    token_digrest = digest_session_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    db_connection.execute(
        insert(User).values(id=user_id)
    )

    savepoint = db_connection.begin_nested()

    session_id = create_auth_session(
        db_connection,
        user_id=user_id,
        token_digest=token_digrest,
        expires_at=expires_at
    )

    stored_session = db_connection.execute(
        select(AuthSession.id).where(
            AuthSession.id == session_id
        )
    ).scalar_one()

    assert stored_session == session_id

    savepoint.rollback()

    result = db_connection.execute(
        select(AuthSession.id).where(AuthSession.id == session_id)
    ).one_or_none()

    assert result is None