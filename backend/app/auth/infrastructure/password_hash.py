import logging

from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import VerificationError, InvalidHashError, HashingError

logger = logging.getLogger(__name__)

password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False

def needs_password_rehash(password_hash: str) -> bool:
    return password_hasher.check_needs_rehash(password_hash)

def verify_and_prepare_rehash(password: str, password_hash: str) -> tuple[bool, str | None]:
    if not verify_password(password, password_hash):
        return False, None
    
    if not needs_password_rehash(password_hash):
        return True, None

    try:
        new_hash = hash_password(password)
        return True, new_hash
    except HashingError:
        logger.warning(
            "Password rehash failed; keeping existing credential",
            exc_info=True
        )

    return True, None