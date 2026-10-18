from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path

from app.auth.password import load_common_passwords
from app.db.engine import create_database_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_database_engine()

    app.state.db_engine = engine

    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)

common_password_file = (
    Path(__file__).resolve().parent
    / "auth"
    / "data"
    / "100k-most-used-passwords-NCSC.txt"
)

app.state.common_passwords = load_common_passwords(
    common_password_file
)

class RegistrationRequest(BaseModel):
    email: str
    password: str

@app.get('/health')
def health_check():
    return {
        "status": "OK",
        "detail": "FastAPI ready."
    }

@app.post("/auth/register")
def register(request: RegistrationRequest):
    raise HTTPException(
        status_code=501,
        detail="Registration endpoint not implemented yet."
    )