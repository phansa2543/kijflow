import re

LOCAL_ATOM = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"

LOCAL_PART_PATTERN = re.compile(
    rf"{LOCAL_ATOM}(?:\.{LOCAL_ATOM})*"
)

DOMAIN_LABEL_PATTERN = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
)

def canonicalize_email(raw_email: str) -> str:
    email = raw_email.strip()

    if not email.isascii():
        raise ValueError("Invalid email")

    if len(email) > 254:
        raise ValueError("Invalid email")

    if email.count("@") != 1:
        raise ValueError("Invalid email")

    local_part, domain = email.split("@")

    if not 1 <= len(local_part) <= 64:
        raise ValueError("Invalid email")

    if not LOCAL_PART_PATTERN.fullmatch(local_part):
        raise ValueError("Invalid email")

    domain_labels = domain.split(".")

    for label in domain_labels:
        if len(label) > 63:
            raise ValueError("Invalid email")

        if not DOMAIN_LABEL_PATTERN.fullmatch(label):
            raise ValueError("Invalid email")

    return email.lower()