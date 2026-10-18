import uuid, pytest, httpx

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import Mock, patch

from sqlalchemy import select, insert, delete, func
from sqlalchemy.exc import IntegrityError

from app.auth.hibp import PasswordScreeningUnavailableError
from app.auth.password_hash import hash_password, verify_password
from app.auth.registration import create_user_with_credential, register_user

from app.models.user import User
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.password_credential import UserPasswordCredential

def test_creates_user_with_password_credential(db_connection):
    password = "ExamplePasswordForTest2026!"
    password_hash = hash_password(password)

    user_id = create_user_with_credential(
        db_connection,
        email="alice@example.com",
        password_hash=password_hash
    )

    created_user_id = db_connection.execute(
        select(User.id).where(User.id == user_id)
    ).scalar_one()

    credential = db_connection.execute(
        select(
            UserPasswordCredential.email,
            UserPasswordCredential.password_hash
        ).where(
            UserPasswordCredential.user_id == user_id
        )
    ).one()

    assert created_user_id == user_id
    assert credential.email == "alice@example.com"
    assert credential.password_hash == password_hash

def test_registration_rolls_back_when_credential_insert_fails(db_connection):
    existing_user_id = uuid.uuid4()

    db_connection.execute(
        insert(User).values(id=existing_user_id)
    )

    db_connection.execute(
        insert(UserPasswordCredential).values(
            user_id=existing_user_id,
            email="alice@example.com",
            password_hash=hash_password("ExistingPassword2026!")
        )
    )

    users_before = db_connection.execute(
        select(func.count()).select_from(User)
    ).scalar_one()

    credentials_before = db_connection.execute(
        select(func.count()).select_from(UserPasswordCredential)
    ).scalar_one()

    with pytest.raises(IntegrityError):
        with db_connection.begin_nested():
            create_user_with_credential(
                db_connection,
                email="alice@example.com",
                password_hash=hash_password("NewPassword2026!")
            )

    users_after = db_connection.execute(
        select(func.count()).select_from(User)
    ).scalar_one()

    credentials_after = db_connection.execute(
        select(func.count()).select_from(UserPasswordCredential)
    ).scalar_one()

    assert users_after == users_before
    assert credentials_after == credentials_before

def test_register_user_integrates_email_screening_and_hashing(engine):
    client = Mock()
    common_passwords = set()

    suffix = uuid.uuid4().hex
    raw_email = f" Alice-{suffix}@Example.COM "
    expected_email = f"alice-{suffix}@example.com"

    raw_password = "Cafe\u0301Secure123!"
    normalized_password = "CaféSecure123!"

    user_id = None

    try:
        with patch(
            "app.auth.registration.screen_password",
            return_value=normalized_password,
        ) as mocked_screen:
            user_id = register_user(
                engine,
                raw_email=raw_email,
                raw_password=raw_password,
                common_passwords=common_passwords,
                client=client,
            )

        with engine.connect() as connection:
            credential = connection.execute(
                select(
                    UserPasswordCredential.email,
                    UserPasswordCredential.password_hash,
                ).where(
                    UserPasswordCredential.user_id == user_id
                )
            ).one()

        assert credential.email == expected_email

        assert verify_password(
            normalized_password,
            credential.password_hash,
        ) is True

        mocked_screen.assert_called_once_with(
            raw_password,
            common_passwords,
            client,
        )

    finally:
        if user_id is not None:
            with engine.begin() as connection:
                connection.execute(
                    delete(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    )
                )

                connection.execute(
                    delete(User).where(User.id == user_id)
                )

def test_registration_does_not_persist_when_screening_fails(engine):
    with engine.connect() as connection:
        users_before = connection.execute(
            select(func.count()).select_from(User)
        ).scalar_one()

        credentials_before = connection.execute(
            select(func.count()).select_from(UserPasswordCredential)
        ).scalar_one()

    with patch(
        "app.auth.registration.screen_password",
        side_effect=ValueError("Password is not allowed"),
    ) as mocked_screen, patch(
        "app.auth.registration.hash_password"
    ) as mocked_hash:

        with pytest.raises(ValueError, match="Password is not allowed"):
            register_user(
                engine,
                raw_email="alice@example.com",
                raw_password="BlockedPassword123!",
                common_passwords=set(),
                client=Mock(),
            )

    with engine.connect() as connection:
        users_after = connection.execute(
            select(func.count()).select_from(User)
        ).scalar_one()

        credentials_after = connection.execute(
            select(func.count()).select_from(UserPasswordCredential)
        ).scalar_one()

    mocked_screen.assert_called_once()
    mocked_hash.assert_not_called()

    assert users_after == users_before
    assert credentials_after == credentials_before

def test_registration_commits_both_records(engine):
    email = f"atomic-{uuid.uuid4().hex}@example.com"
    password = "AtomicRegistration2026!"
    user_id = None

    try:
        with patch(
            "app.auth.registration.screen_password",
            return_value=password
            ):
                with engine.connect() as connection:
                    organizations_before = connection.execute(
                        select(func.count()).select_from(Organization)
                    ).scalar_one()

                    memberships_before = connection.execute(
                        select(func.count()).select_from(Membership)
                    ).scalar_one()
            
                user_id = register_user(
                    engine,
                    raw_email=email,
                    raw_password=password,
                    common_passwords=set(),
                    client=Mock()
                )

        with engine.connect() as connection:
            created_user_id = connection.execute(
                select(User.id).where(User.id == user_id)
            ).scalar_one()

            credential = connection.execute(
                select(
                    UserPasswordCredential.email,
                    UserPasswordCredential.password_hash
                ).where(
                    UserPasswordCredential.user_id == user_id
                )
            ).one()

        assert created_user_id == user_id
        assert credential.email == email
        assert verify_password(
            password,
            credential.password_hash
        ) is True

        with engine.connect() as connection:
            organizations_after = connection.execute(
                select(func.count()).select_from(Organization)
            ).scalar_one()

            memberships_after = connection.execute(
                select(func.count()).select_from(Membership)
            ).scalar_one()

        assert organizations_after == organizations_before
        assert memberships_after == memberships_before

    finally:
        if user_id is not None:
            with engine.begin() as connection:
                connection.execute(
                    delete(UserPasswordCredential).where(
                        UserPasswordCredential.user_id == user_id
                    )
                )

                connection.execute(
                    delete(User).where(User.id == user_id)
                )

def test_registration_rolls_back_on_duplicate_email(engine):
    email = f"duplicate-{uuid.uuid4().hex}@example.com"
    existing_user_id = uuid.uuid4()
    password = "NewSecurePassword2026!"

    with engine.begin() as connection:
        connection.execute(
            insert(User).values(id=existing_user_id)
        )

        connection.execute(
            insert(UserPasswordCredential).values(
                user_id=existing_user_id,
                email=email,
                password_hash=hash_password("ExistingPassword2026!")
            )
        )

    try:
        with engine.connect() as connection:
            users_before = connection.execute(
                select(func.count()).select_from(User)
            ).scalar_one()

            credentials_before = connection.execute(
                select(func.count()).select_from(UserPasswordCredential)
            ).scalar_one()

        with patch(
            "app.auth.registration.screen_password",
            return_value=password
        ):
            with pytest.raises(IntegrityError):
                register_user(
                    engine,
                    raw_email=f" {email.upper()} ",
                    raw_password=password,
                    common_passwords=set(),
                    client=Mock()
                )

        with engine.connect() as connection:
            users_after = connection.execute(
                select(func.count()).select_from(User)
            ).scalar_one()

            credentials_after = connection.execute(
                select(func.count()).select_from(UserPasswordCredential)
            ).scalar_one()

            origin_credential = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalar_one()

        assert users_after == users_before
        assert credentials_after == credentials_before
        assert origin_credential == existing_user_id

    finally:
        with engine.begin() as connection:
            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == existing_user_id
                )
            )

            connection.execute(
                delete(User).where(User.id == existing_user_id)
            )

def test_concurrent_registration_same_email_creates_one_account(engine):
    email = f"concurrent-{uuid.uuid4().hex}@example.com"
    password = "ConcurrentPassword2026!"

    barrier = Barrier(2, timeout=10)

    with engine.connect() as connection:
        users_before = set(
            connection.execute(select(User.id)).scalars().all()
        )

    original_create = create_user_with_credential

    def synchronized_create(connection, *, email, password_hash):
        barrier.wait()

        return original_create(
            connection,
            email=email,
            password_hash=password_hash,
        )

    def attempt_registration():
        try:
            user_id = register_user(
                engine,
                raw_email=email,
                raw_password=password,
                common_passwords=set(),
                client=Mock(),
            )

            return ("success", user_id)

        except IntegrityError:
            return ("duplicate", None)

    try:
        with patch(
            "app.auth.registration.screen_password",
            return_value=password,
        ), patch(
            "app.auth.registration.create_user_with_credential",
            side_effect=synchronized_create,
        ):
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(attempt_registration)
                    for _ in range(2)
                ]

                results = [
                    future.result(timeout=15)
                    for future in futures
                ]

        statuses = sorted(result[0] for result in results)

        assert statuses == ["duplicate", "success"]

        with engine.connect() as connection:
            credential_user_ids = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalars().all()

            users_after = set(
                connection.execute(select(User.id)).scalars().all()
            )

        assert len(credential_user_ids) == 1
        assert len(users_after - users_before) == 1

    finally:
        with engine.begin() as connection:
            user_ids = connection.execute(
                select(UserPasswordCredential.user_id).where(
                    UserPasswordCredential.email == email
                )
            ).scalars().all()

            connection.execute(
                delete(UserPasswordCredential).where(
                    UserPasswordCredential.email == email
                )
            )

            if user_ids:
                connection.execute(
                    delete(User).where(
                        User.id.in_(user_ids)
                    )
                )

def test_registration_rejects_invalid_email_before_processing(engine):
    with patch(
        "app.auth.registration.screen_password"
    ) as mocked_screen, patch(
        "app.auth.registration.hash_password"
    ) as mocked_hash, patch.object(
        engine, "begin"
    ) as mocked_begin:

        with pytest.raises(ValueError, match="Invalid email"):
            register_user(
                engine,
                raw_email="invalid-email",
                raw_password="ExamplePassword2026!",
                common_passwords=set(),
                client=Mock(),
            )

    mocked_screen.assert_not_called()
    mocked_hash.assert_not_called()
    mocked_begin.assert_not_called()

def test_registration_fails_closed_when_hibp_unavailable(engine):
    client = Mock()
    client.get.side_effect = httpx.ReadTimeout(
        "Simulated HIBP timeout"
    )

    with patch(
        "app.auth.registration.hash_password"
    ) as mocked_hash, patch.object(
        engine, "begin"
    ) as mocked_begin:

        with pytest.raises(
            PasswordScreeningUnavailableError,
            match="Password screening temporarily unavailable",
        ):
            register_user(
                engine,
                raw_email="hibp-test@example.com",
                raw_password="UniqueSecurePassword2026!",
                common_passwords=set(),
                client=client,
            )

    client.get.assert_called_once()
    mocked_hash.assert_not_called()
    mocked_begin.assert_not_called()