import httpx

from app.auth.password import prepare_password, is_common_password
from app.auth.hibp import is_password_compromised

def screen_password(
        raw_password: str,
        common_passwords: set[str],
        client: httpx.Client
) -> str:
    password = prepare_password(raw_password)

    if is_common_password(password, common_passwords):
        raise ValueError("Password is not allowed")

    if is_password_compromised(password, client):
        raise ValueError("Password is not allowed")

    return password