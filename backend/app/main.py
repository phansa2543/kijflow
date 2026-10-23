import httpx, os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

from app.auth.infrastructure.common_passwords import load_common_passwords
from app.auth.infrastructure.password_hash import hash_password
from app.auth.infrastructure.login_counter_identifier import load_login_counter_hmac_secret

from app.auth.presentation.routes import router as auth_router
from app.auth.presentation.login_route import login_router

from app.db.engine import create_database_engine

def read_positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))

    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"Invalid configuration: {name}") from None

    if value <= 0:
        raise ValueError(f"Invalid configuration: {name}")

    return value

@asynccontextmanager
async def lifespan(app: FastAPI):
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    load_login_counter_hmac_secret()

    source_limit = read_positive_int("LOGIN_SOURCE_LIMIT", 30)
    source_window = read_positive_int("LOGIN_SOURCE_WINDOW_SECONDS", 60)
    account_limit = read_positive_int("LOGIN_ACCOUNT_LIMIT", 10)
    account_window = read_positive_int("LOGIN_ACCOUNT_WINDOW_SECONDS", 900)

    engine = create_database_engine()

    try:
        with httpx.Client() as hibp_client:
            app.state.db_engine = engine
            app.state.hibp_client = hibp_client
            app.state.registration_rate_limit_threshold = 10
            app.state.registration_rate_limit_window_seconds = 900
            app.state.dummy_password_hash = hash_password(
                "kijflow-login-dummy-password-not-a-real-credential"
            )
            app.state.login_source_limit = source_limit
            app.state.login_source_window_seconds = source_window
            app.state.login_account_limit = account_limit
            app.state.login_account_window_seconds = account_window
            yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(login_router)

common_password_file = (
    Path(__file__).resolve().parent
    / "auth"
    / "data"
    / "100k-most-used-passwords-NCSC.txt"
)

app.state.common_passwords = load_common_passwords(
    common_password_file
)

@app.get('/health')
def health_check():
    return {
        "status": "OK",
        "detail": "FastAPI ready."
    }