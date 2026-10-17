import unicodedata, hashlib

from pathlib import Path

def normalize_password(raw_password: str) -> str:
    return unicodedata.normalize("NFC", raw_password)

def prepare_password(raw_password: str) -> str:
    result = normalize_password(raw_password)

    if len(result) < 8:
        raise ValueError("Password is too short")

    if len(result) > 128:
        raise ValueError("Password is too long")

    return result

def is_common_password(password: str, common_passwords: set[str]) -> bool:
    return password in common_passwords

def load_common_passwords(file_path: Path) -> set[str]:
    content = file_path.read_text(encoding="utf-8")
    passwords = {
        normalize_password(line)
        for line in content.splitlines()
        if line
    }

    if not passwords:
        raise ValueError("Common password dataset is empty")

    return passwords

def get_password_sha1(password: str) -> str:
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

def get_password_hash_parts(password: str) -> tuple[str, str]:
    password_hash = get_password_sha1(password)

    prefix = password_hash[:5]
    suffix = password_hash[5:]

    return prefix, suffix