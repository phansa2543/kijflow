import uuid, pytest
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from sqlalchemy import insert, update, delete, text
from sqlalchemy.exc import OperationalError

from app.models.user import User
from app.models.password_credential import UserPasswordCredential

from app.auth.infrastructure.login_persistence import lock_and_validate_credential

def test_credential_row_lock_blocks_concurrent_update(engine):
    user_id = uuid.uuid4()
    email = f"lock-concurrency-{uuid.uuid4().hex}@example.com"
    old_hash = "original-hash"
    new_hash = "changed-hash"

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

    lock_acquired = Event()
    release_lock = Event()

    def transaction_a():
        with engine.begin() as connection:
            valid = lock_and_validate_credential(
                connection,
                user_id=user_id,
                expected_hash=old_hash
            )

            assert valid is True

            lock_acquired.set()

            if not release_lock.wait(timeout=15):
                raise TimeoutError("Timed out waiting to release credential lock")

    def transaction_b():
        if not lock_acquired.wait(timeout=10):
            raise TimeoutError("Time out waiting for credential lock")

        with engine.begin() as connection:
            connection.execute(
                text("SET LOCAL lock_timeout = '2s'")
            )

            connection.execute(
                update(UserPasswordCredential).where(
                    UserPasswordCredential.user_id == user_id
                ).values(password_hash=new_hash)
            )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_a = executor.submit(transaction_a)
            assert lock_acquired.wait(timeout=10)
            
            future_b = executor.submit(transaction_b)

            try:
                with pytest.raises(OperationalError) as exc_info:
                    future_b.result(timeout=10)
                assert exc_info.value.orig.sqlstate == "55P03"
            finally:
                release_lock.set()

            future_a.result(timeout=10)
    finally:
        release_lock.set()

        with engine.begin() as connection:
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