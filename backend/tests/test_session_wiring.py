import uuid
from datetime import timedelta

from sqlalchemy import insert, select, delete

from app.models.user import User
from app.models.password_credential import UserPasswordCredential
from app.models.auth_session import AuthSession

from app.auth.infrastructure.session_wiring import make_session_creation_handler
from app.auth.infrastructure.session_token import digest_session_token

def test_session_creation_success(engine):
    user_id = uuid.uuid4()
    email = f"session-{uuid.uuid4().hex}@example.com"
    expected_hash = "verified-hash"

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=expected_hash
            )
        )

    try:
        handler = make_session_creation_handler(
            engine=engine,
            session_lifetime=timedelta(hours=24)
        )

        token = handler(user_id, expected_hash)

        assert isinstance(token, str)
        assert token

        with engine.begin() as connection:
            result = connection.execute(
                select(
                    AuthSession.user_id,
                    AuthSession.token_digest,
                    AuthSession.expires_at,
                    AuthSession.revoked_at
                ).where(
                    AuthSession.user_id == user_id
                )
            ).one()

        assert result.user_id == user_id
        assert result.token_digest == digest_session_token(token)
        assert result.expires_at is not None
        assert result.revoked_at is None
        
    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(AuthSession).where(
                    AuthSession.user_id == user_id
                )
            )

            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id)
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )

def test_session_creation_stale_hash(engine):
    user_id = uuid.uuid4()
    email = f"session-stale-{uuid.uuid4().hex}@example.com"
    stored_hash = "current-hash"
    expected_hash = "old-hash"

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=stored_hash
            )
        )

    try:
        handler = make_session_creation_handler(
            engine=engine,
            session_lifetime=timedelta(hours=24)
        )

        token = handler(user_id, expected_hash)

        assert token is None

        with engine.begin() as connection:
            session = connection.execute(
                select(AuthSession.id).where(
                    AuthSession.user_id == user_id
                )
            ).one_or_none()

        assert session is None

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(AuthSession).where(
                    AuthSession.user_id == user_id
                )
            )

            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )

def test_session_creation_unknown_user(engine):
    user_id = uuid.uuid4()
    expected_hash = "some-hash"

    handler = make_session_creation_handler(
        engine=engine,
        session_lifetime=timedelta(hours=24)
    )

    token = handler(user_id, expected_hash)

    assert token is None

    with engine.begin() as connection:
        session = connection.execute(
            select(AuthSession.id).where(
                AuthSession.user_id == user_id
            )
        ).one_or_none()

    assert session is None