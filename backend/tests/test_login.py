import uuid
from unittest.mock import Mock

from app.auth.application.login import authenticate_user

def test_authenticate_user_success():
    user_id = uuid.uuid4()

    find_credential = Mock(
        return_value=(user_id, "store-hash")
    )

    verify_password = Mock(
        return_value=(True, None)
    )

    result = authenticate_user(
        raw_email="  USER@Example.COM  ",
        raw_password="correct-password",
        find_credential=find_credential,
        verify_password=verify_password,
        dummy_password_hash="dummy-hash"
    )

    assert result == (user_id, "store-hash", None)

def test_authenticate_user_wrong_password():
    user_id = uuid.uuid4()

    find_credential = Mock(
        return_value=(user_id, "stored-hash")
    )

    verify_password = Mock(
        return_value=(False, None)
    )

    result = authenticate_user(
        raw_email="  USER@Example.COM  ",
        raw_password="wrong-password",
        find_credential=find_credential,
        verify_password=verify_password,
        dummy_password_hash="dummy-hash"
    )

    assert result is None

    find_credential.assert_called_once_with("user@example.com")
    verify_password.assert_called_once_with("wrong-password", "stored-hash")

def test_authenticate_user_unknown_email():
    find_credential = Mock(return_value=None)
    verify_password = Mock(return_value=(False, None))

    result = authenticate_user(
        raw_email="missing@example.com",
        raw_password="some-password",
        find_credential=find_credential,
        verify_password=verify_password,
        dummy_password_hash="dummy-hash"
    )

    assert result is None
    
    find_credential.assert_called_once_with("missing@example.com")
    verify_password.assert_called_once_with("some-password", "dummy-hash")

def test_authenticate_user_unknown_email_dummy_verifies():
    find_credential = Mock(return_value=None)
    verify_password = Mock(return_value=(True, None))

    result = authenticate_user(
        raw_email="missing@example.com",
        raw_password="some-password",
        find_credential=find_credential,
        verify_password=verify_password,
        dummy_password_hash="dummy-hash"
    )

    assert result is None

    find_credential.assert_called_once_with("missing@example.com")
    verify_password.assert_called_once_with("some-password", "dummy-hash")

def test_authenticate_user_success_with_rehash():
    user_id = uuid.uuid4()

    find_credential = Mock(
        return_value=(user_id, "old-hash")
    )

    verify_password = Mock(
        return_value=(True, "new-hash")
    )

    result = authenticate_user(
        raw_email="user@example.com",
        raw_password="correct-password",
        find_credential=find_credential,
        verify_password=verify_password,
        dummy_password_hash="dummy-hash"
    )

    assert result == (user_id, "old-hash", "new-hash")

    find_credential.assert_called_once_with("user@example.com")
    verify_password.assert_called_once_with("correct-password", "old-hash")