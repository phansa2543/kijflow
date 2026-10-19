from collections.abc import Callable

from app.auth.domain.password import prepare_password

from app.auth.application.errors import PasswordRejected

def screen_password_with_checkers(
        raw_password: str,
        *,
        is_common: Callable[[str], bool],
        is_compromised: Callable[[str], bool]
) -> str:
    password = prepare_password(raw_password)

    if is_common(password):
        raise PasswordRejected("Password is not allowed")

    if is_compromised(password):
        raise PasswordRejected("Password is not allowed")

    return password