import unicodedata

def normalize_password(raw_password: str) -> str:
    return unicodedata.normalize("NFC", raw_password)

def prepare_password(raw_password: str) -> str:
    result = normalize_password(raw_password)

    if len(result) < 8:
        raise ValueError("Password is too short")

    if len(result) > 128:
        raise ValueError("Password is too long")

    return result