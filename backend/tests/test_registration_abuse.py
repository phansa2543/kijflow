import pytest
from unittest.mock import Mock

from app.auth.application.errors import (
    RegistrationRateLimited,
    RegistrationLimiterUnavailable,
)
from app.auth.application.registration_abuse import (
    enforce_registration_attempt_limit,
)


def test_registration_attempt_allowed():
    consume = Mock(return_value=(True, 900))

    result = enforce_registration_attempt_limit(
        consume_attempt=consume,
    )

    assert result is None
    consume.assert_called_once_with()


def test_registration_attempt_rejected():
    consume = Mock(return_value=(False, 120))

    with pytest.raises(RegistrationRateLimited) as exc_info:
        enforce_registration_attempt_limit(
            consume_attempt=consume,
        )

    assert exc_info.value.retry_after_seconds == 120
    consume.assert_called_once_with()


def test_registration_limiter_unavailable_propagates():
    consume = Mock(
        side_effect=RegistrationLimiterUnavailable()
    )

    with pytest.raises(RegistrationLimiterUnavailable):
        enforce_registration_attempt_limit(
            consume_attempt=consume,
        )

    consume.assert_called_once_with()