from pathlib import Path

from app.auth.domain.password import normalize_password


def is_common_password(
    password: str,
    common_passwords: set[str],
) -> bool:
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