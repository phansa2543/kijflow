import unicodedata

def normalize_password(raw_password: str) -> str:
    return unicodedata.normalize("NFC", raw_password)