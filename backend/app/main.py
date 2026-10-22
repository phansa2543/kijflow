import httpx

from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path

from app.auth.infrastructure.common_passwords import load_common_passwords
from app.auth.infrastructure.password_hash import hash_password

from app.auth.presentation.routes import router as auth_router
from app.auth.presentation.login_route import login_router

from app.db.engine import create_database_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
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