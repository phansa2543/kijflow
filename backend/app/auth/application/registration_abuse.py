from collections.abc import Callable

from app.auth.application.errors import RegistrationRateLimited


def enforce_registration_attempt_limit(
    *,
    consume_attempt: Callable[[], tuple[bool, int]],
) -> None:
    allowed, retry_after_seconds = consume_attempt()

    if not allowed:
        raise RegistrationRateLimited(retry_after_seconds)