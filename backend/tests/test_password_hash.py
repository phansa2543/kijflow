from unittest.mock import patch

from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import HashingError, VerificationError

from app.auth.password_hash import hash_password, verify_password, needs_password_rehash, verify_and_prepare_rehash
from app.auth.password import normalize_password

def test_hash_password_uses_approved_argon2id_policy():
    password = "ExamplePasswordForTest2026!"

    password_hash = hash_password(password)

    assert password_hash.startswith(
        "$argon2id$v=19$m=19456,t=2,p=1$"
    )
    assert password_hash != password

def test_verify_password_accepts_correct_password():
    password = "ExamplePasswordForTest2026!"
    password_hash = hash_password(password)

    result = verify_password(password, password_hash)

    assert result is True

def test_verify_password_rejects_wrong_password():
    password = "ExamplePasswordForTest2026!"
    password_hash = hash_password(password)

    result = verify_password("WrongPassword2026!", password_hash)

    assert result is False

def test_verify_password_rejects_malformed_hash():
    password = "ExamplePasswordForTest2026!"
    malformed_hash = "not-a-valid-argon2-hash"

    result = verify_password(password, malformed_hash)

    assert result is False

def test_hash_password_generates_unique_salt():
    password = "ExamplePasswordForTest2026!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True

def test_password_hash_supports_nfc_equivalent_inputs():
    composed = "Café-2026-Strong!"
    decomposed = "Cafe\u0301-2026-Strong!"

    assert composed != decomposed

    password_hash = hash_password(
        normalize_password(decomposed)
    )

    result = verify_password(
        normalize_password(composed),
        password_hash
    )

    assert result is True

def test_password_hash_detects_outdated_parameters():
    password = "ExamplePasswordForTest2026!"

    current_hash = hash_password(password)

    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=19456,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )

    old_hash = old_hasher.hash(password)

    assert verify_password(password, old_hash) is True
    assert needs_password_rehash(current_hash) is False
    assert needs_password_rehash(old_hash) is True

def test_failed_authentication_never_rehashes():
    password = "CorrectPassword2026!"

    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=19456,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )

    old_hash = old_hasher.hash(password)

    with patch("app.auth.password_hash.hash_password") as mocked_hash:
        authenticated, replacement_hash = verify_and_prepare_rehash(
            "WrongPassword2026!",
            old_hash
        )

    assert authenticated is False
    assert replacement_hash is None
    mocked_hash.assert_not_called()

def test_successful_authentication_aith_current_hash_does_not_rehash():
    password = "ExamplePasswordForTest2026!"
    current_hash = hash_password(password)

    with patch("app.auth.password_hash.hash_password") as mocked_hash:
        authenticated, replacement_hash = verify_and_prepare_rehash(
            password,
            current_hash
        )

    assert authenticated is True
    assert replacement_hash is None
    mocked_hash.assert_not_called()

def test_successful_authenticateion_with_old_hash_prepares_rehash():
    password = "ExamplePasswordForTest2026!"

    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=19456,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )

    old_hash = old_hasher.hash(password)

    authenticated, replacement_hash = verify_and_prepare_rehash(password, old_hash)

    assert authenticated is True
    assert replacement_hash is not None

    assert needs_password_rehash(replacement_hash) is False

    assert verify_password(password, replacement_hash) is True

    assert verify_password(password, old_hash) is True

    assert replacement_hash != old_hash

def test_rehash_failure_does_not_block_valid_authentication():
    password = "ExamplePasswordForTest2026!"

    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=19456,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID
    )

    old_hash = old_hasher.hash(password)

    with patch(
        "app.auth.password_hash.hash_password",
        side_effect=HashingError("Simulated rehash failure")
    ) as mocked_hash:
        authenticated, replacement_hash = verify_and_prepare_rehash(password, old_hash)

    assert authenticated is True
    assert replacement_hash is None

    mocked_hash.assert_called_once_with(password)

    assert verify_password(password, old_hash) is True

def test_verify_password_rejects_corrupted_argon2_hash():
    password = "ExamplePasswordForTest2026!"
    valid_hash = hash_password(password)

    corrupted_hash = valid_hash[:-1] + "!"

    assert verify_password(password, corrupted_hash) is False

def test_verify_password_handles_verification_error():
    password = "ExamplePasswordForTest2026!"
    corrupted_hash = "corrupted-argon2-hash"

    with patch("app.auth.password_hash.password_hasher") as mocked_hasher:
        mocked_hasher.verify.side_effect = VerificationError("Simulated decoding failure")
        result = verify_password(password, corrupted_hash)

        assert result is False

        mocked_hasher.verify.assert_called_once_with(
            corrupted_hash,
            password
        )