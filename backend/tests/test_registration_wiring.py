import pytest, uuid

from unittest.mock import Mock, patch

from app.auth.application.errors import PasswordRejected, RegistrationRateLimited

from app.auth.infrastructure.registration_wiring import (
    make_registration_handler,
    make_registration_limit_checker
)

def test_registration_wiring_passes_dependencies_to_use_case():
    engine = Mock()
    hibp_client = Mock()
    common_passwords = {"blockedpassword123"}

    with (
        patch(
            "app.auth.infrastructure.registration_wiring.register_user"
        ) as mocked_register,
        patch(
            "app.auth.infrastructure.registration_wiring.hash_password"
        ) as mocked_hash,
    ):
        handler = make_registration_handler(
            engine=engine,
            common_passwords=common_passwords,
            hibp_client=hibp_client,
        )

        handler("alice@example.com", "ExamplePassword123!")

    mocked_register.assert_called_once()

    kwargs = mocked_register.call_args.kwargs

    assert kwargs["raw_email"] == "alice@example.com"
    assert kwargs["raw_password"] == "ExamplePassword123!"

    assert callable(kwargs["screen"])
    assert callable(kwargs["persist"])
    assert kwargs["hash_password"] is mocked_hash

    with pytest.raises(PasswordRejected):
        kwargs["screen"]("blockedpassword123")

    with patch(
        "app.auth.infrastructure.hibp.is_password_compromised",
        return_value=False,
    ) as mocked_hibp:
        assert kwargs["screen"]("ExamplePassword123!") == "ExamplePassword123!"
        mocked_hibp.assert_called_once_with(
            "ExamplePassword123!",
            hibp_client,
        )

def test_registration_wiring_persists_through_injected_engine():
    engine = Mock()
    hibp_client = Mock()
    expected_user_id = uuid.uuid4()

    with (
        patch(
            "app.auth.infrastructure.registration_wiring.register_user"
        ) as mocked_register,
        patch(
            "app.auth.infrastructure.registration_wiring.persist_new_user_with_credential",
            return_value=expected_user_id,
        ) as mocked_persist,
    ):
        handler = make_registration_handler(
            engine=engine,
            common_passwords=set(),
            hibp_client=hibp_client,
        )

        handler("alice@example.com", "ExamplePassword123!")

        persist = mocked_register.call_args.kwargs["persist"]
        result = persist("alice@example.com", "hashed-password")

    assert result == expected_user_id

    mocked_persist.assert_called_once_with(
        engine,
        email="alice@example.com",
        password_hash="hashed-password",
    )

def test_registration_limit_wiring_allows_attempt():
    engine = Mock()

    with patch(
        "app.auth.infrastructure.registration_wiring.consume_registration_attempt",
        return_value=(True, 900),
    ) as mocked_consume:
        checker = make_registration_limit_checker(
            engine=engine,
            client_ip="192.0.2.10",
            threshold=10,
            window_seconds=900,
        )

        assert checker() is None

    mocked_consume.assert_called_once_with(
        engine=engine,
        client_ip="192.0.2.10",
        threshold=10,
        window_seconds=900,
    )

def test_registration_limit_wiring_rejects_attempt():
    engine = Mock()

    with patch(
        "app.auth.infrastructure.registration_wiring.consume_registration_attempt",
        return_value=(False, 120),
    ) as mocked_consume:
        checker = make_registration_limit_checker(
            engine=engine,
            client_ip="192.0.2.10",
            threshold=10,
            window_seconds=900,
        )

        with pytest.raises(RegistrationRateLimited) as exc_info:
            checker()

    assert exc_info.value.retry_after_seconds == 120

    mocked_consume.assert_called_once_with(
        engine=engine,
        client_ip="192.0.2.10",
        threshold=10,
        window_seconds=900,
    )