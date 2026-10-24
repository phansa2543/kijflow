from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status


def normalize_trusted_origin(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Invalid trusted frontend origin")

    if (
        value != value.strip()
        or any(ord(char) <= 32 or ord(char) == 127 for char in value)
        or "\\" in value
        or "%" in value
        or "," in value
    ):
        raise ValueError("Invalid trusted frontend origin")

    try:
        parts = urlsplit(value)
        hostname = parts.hostname
        port = parts.port
    except ValueError:
        raise ValueError("Invalid trusted frontend origin") from None

    if (
        parts.scheme not in ("http", "https")
        or not hostname
        or parts.username is not None
        or parts.password is not None
        or parts.path
        or parts.query
        or parts.fragment
        or hostname.endswith(".")
        or port == 0
    ):
        raise ValueError("Invalid trusted frontend origin")

    host = hostname.lower()

    if ":" in host:
        host = f"[{host}]"

    if port is None:
        normalized = f"{parts.scheme.lower()}://{host}"
    else:
        normalized = f"{parts.scheme.lower()}://{host}:{port}"

    if parts.scheme == "http" and hostname not in (
        "localhost",
        "127.0.0.1",
    ):
        raise ValueError("HTTP trusted origin must be local")

    if value.lower() != normalized:
        raise ValueError("Invalid trusted frontend origin")

    return normalized

def require_trusted_origin(request: Request) -> None:
    origins = request.headers.getlist("origin")

    if len(origins) != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin not allowed",
        )

    try:
        normalized = normalize_trusted_origin(origins[0])
    except ValueError:
        normalized = None

    if normalized != request.app.state.trusted_frontend_origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin not allowed",
        )