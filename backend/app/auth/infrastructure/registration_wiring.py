from collections.abc import Callable
from functools import partial
from uuid import UUID

import httpx
from sqlalchemy.engine import Engine

from app.auth.application.registration_abuse import enforce_registration_attempt_limit
from app.auth.application.registration import register_user
from app.auth.application.password_screening import (
    screen_password_with_checkers,
)

from app.auth.infrastructure.registration_rate_limit import consume_registration_attempt
from app.auth.infrastructure.common_passwords import is_common_password
from app.auth.infrastructure.hibp import make_compromised_checker
from app.auth.infrastructure.password_hash import hash_password
from app.auth.infrastructure.registration_persistence import (
    persist_new_user_with_credential,
)


def make_registration_handler(
    *,
    engine: Engine,
    common_passwords: set[str],
    hibp_client: httpx.Client,
) -> Callable[[str, str], UUID]:
    def screen(password: str) -> str:
        return screen_password_with_checkers(
            password,
            is_common=partial(is_common_password, common_passwords=common_passwords),
            is_compromised=make_compromised_checker(hibp_client),
        )

    def persist(email: str, password_hash: str) -> UUID:
        return persist_new_user_with_credential(
            engine,
            email=email,
            password_hash=password_hash,
        )

    def handler(email: str, password: str) -> UUID:
        return register_user(
            raw_email=email,
            raw_password=password,
            screen=screen,
            hash_password=hash_password,
            persist=persist,
        )

    return handler

def make_registration_limit_checker(
    *,
    engine: Engine,
    client_ip: str,
    threshold: int,
    window_seconds: int,
) -> Callable[[], None]:

    def check() -> None:
        enforce_registration_attempt_limit(
            consume_attempt=lambda: consume_registration_attempt(
                engine=engine,
                client_ip=client_ip,
                threshold=threshold,
                window_seconds=window_seconds,
            ),
        )

    return check