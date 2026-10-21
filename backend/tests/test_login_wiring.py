import uuid

from argon2 import PasswordHasher
from argon2.low_level import Type

from sqlalchemy import insert, delete, select, update

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

import app.auth.infrastructure.login_wiring as login_wiring
from app.auth.infrastructure.login_wiring import make_login_handler
from app.auth.infrastructure.password_hash import hash_password

def test_login_handler_success(engine):
    user_id = uuid.uuid4()
    email = f"login-{uuid.uuid4().hex}@example.com"
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
        handler = make_login_handler(
            engine=engine,
            dummy_password_hash=hash_password("dummy-password")
        )

        result = handler(email, password)

        assert result == (user_id, password_hash)

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )

def test_login_handler_wrong_password(engine):
    user_id = uuid.uuid4()
    email = f"login-wrong-{uuid.uuid4().hex}@example.com"
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
        handler = make_login_handler(
            engine=engine,
            dummy_password_hash=password_hash
        )

        result = handler(email, wrong_password)

        assert result is None

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )

def test_login_handler_unknown_email(engine):
    email = f"unknown-{uuid.uuid4().hex}@example.com"
    password = "some-password"
    dummy_hash = hash_password("dummy-password")

    with engine.begin() as connection:
        handler = make_login_handler(
            engine=engine,
            dummy_password_hash=dummy_hash
        )

        result = handler(email, password)

    assert result is None

def test_login_handler_rehash_success(engine):
    user_id = uuid.uuid4()
    email = f"login-rehash-{uuid.uuid4().hex}@example.com"
    password = "correct-password"
    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=8192,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )
    old_hash = old_hasher.hash(password)

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
        handler = make_login_handler(
            engine=engine,
            dummy_password_hash="dummy-password"
        )

        result = handler(email, password)

        assert result is not None

        authenticated_user_id, expected_hash = result

        assert authenticated_user_id == user_id
        assert expected_hash != old_hash

        with engine.begin() as connection:
            stored_hash = connection.execute(
                select(UserPasswordCredential.password_hash).where(
                    UserPasswordCredential.user_id == user_id
                )
            ).scalar_one()

        assert stored_hash == expected_hash

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )

def test_login_handler_rehash_cas_failure(engine, monkeypatch):
    user_id = uuid.uuid4()
    email = f"login-race-{uuid.uuid4().hex}@example.com"
    password = "correct-password"
    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=8192,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )
    old_hash = old_hasher.hash(password)
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
        original_verify = login_wiring.verify_and_prepare_rehash

        def verify_then_change(password, password_hash):
            result = original_verify(password, password_hash)
            with engine.begin() as connection:
                connection.execute(
                    update(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    ).values(password_hash=new_hash)
                )
            return result

        monkeypatch.setattr(
            login_wiring,
            "verify_and_prepare_rehash",
            verify_then_change
        )

        handler = make_login_handler(
            engine=engine,
            dummy_password_hash=hash_password("dummy-password")
        )

        result = handler(email, password)

        assert result is None

        with engine.begin() as connection:
            stored_hash = connection.execute(
                select(UserPasswordCredential.password_hash).where(
                    UserPasswordCredential.user_id == user_id
                )
            ).scalar_one()

        assert stored_hash == new_hash

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == user_id)
            )