import uuid
from datetime import timedelta, timezone, datetime

from sqlalchemy import insert, select, delete, update

from app.models.user import User
from app.models.password_credential import UserPasswordCredential
from app.models.auth_session import AuthSession

from app.auth.infrastructure.login_wiring import make_login_handler
from app.auth.infrastructure.session_wiring import make_session_creation_handler
from app.auth.infrastructure.password_hash import hash_password
from app.auth.infrastructure.session_token import digest_session_token

def test_login_creates_session(engine):
    user_id = uuid.uuid4()
    email = f"login-session-{uuid.uuid4().hex}@example.com"
    password = "correct-password"
    password_hash = hash_password(password)

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=password_hash
            )
        )

    try:
        login_handler = make_login_handler(
            engine=engine,
            dummy_password_hash=hash_password("dummy-password")
        )

        session_handler = make_session_creation_handler(
            engine=engine,
            session_lifetime=timedelta(hours=24)
        )

        login_result = login_handler(email, password)

        assert login_result is not None

        authenticated_user_id, expected_hash = login_result

        assert authenticated_user_id == user_id

        token = session_handler(authenticated_user_id, expected_hash)

        assert isinstance(token, str)
        assert token

        with engine.begin() as connection:
            session = connection.execute(
                select(
                    AuthSession.user_id,
                    AuthSession.token_digest,
                    AuthSession.expires_at,
                    AuthSession.revoked_at
                ).where(
                    AuthSession.user_id == user_id
                )
            ).one()

        assert session.user_id == user_id
        assert session.token_digest == digest_session_token(token)
        assert session.revoked_at is None
        assert session.expires_at > datetime.now(timezone.utc)

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

def test_login_wrong_password_does_not_create_session(engine):
    user_id = uuid.uuid4()
    email = f"login-session-wrong-{uuid.uuid4().hex}@example.com"
    password = "correct-password"
    wrong_password = "wrong-password"
    password_hash = hash_password(password)

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=password_hash
            )
        )

    try:
        login_handler = make_login_handler(
            engine=engine,
            dummy_password_hash=hash_password("dummy-password")   
        )

        login_result = login_handler(email, wrong_password)

        assert login_result is None

        with engine.begin() as connection:
            session = connection.execute(
                select(
                    AuthSession.id,
                ).where(
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

def test_credential_change_before_session_creation(engine):
    user_id = uuid.uuid4()
    email = f"login-session-change-{uuid.uuid4().hex}@example.com"
    password = "correct-password"
    old_hash = hash_password(password)
    new_hash = hash_password("changed-password")

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=user_id,
                email=email,
                password_hash=old_hash
            )
        )

    try:
        login_handler = make_login_handler(
            engine=engine,
            dummy_password_hash=hash_password("dummy-password")
        )

        session_handler = make_session_creation_handler(
            engine=engine,
            session_lifetime=timedelta(hours=24)
        )

        result_login_handler = login_handler(email, password)

        assert result_login_handler is not None

        authenticated_user_id, expected_hash = result_login_handler

        assert authenticated_user_id == user_id
        assert expected_hash == old_hash

        with engine.begin() as connection:
            connection.execute(
                update(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                ).values(
                    password_hash = new_hash
                )
            )

        token = session_handler(authenticated_user_id, expected_hash)

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
                delete(User).where(
                    User.id == user_id
                )
            )