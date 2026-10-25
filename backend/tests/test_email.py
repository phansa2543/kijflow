import pytest

from app.auth.domain.email import canonicalize_email
from app.auth.domain.validation_errors import InvalidEmail

def test_canonicalize_email_lowercase():
    raw_email = "Alice@example.com"
    expected = "alice@example.com"

    actual = canonicalize_email(raw_email)

    assert actual == expected

def test_canonicalize_email_trim_whitespace():
    raw_email = " Alice@example.com "
    expected = "alice@example.com"

    actual = canonicalize_email(raw_email)

    assert actual == expected

def test_canonicalize_email_preserves_plus_and_dot():
    raw_email = "Alice.Smith+Sales@Example.COM"
    expected = "alice.smith+sales@example.com"

    actual = canonicalize_email(raw_email)

    assert actual == expected

def test_canonicalize_email_rejects_consecutive_dots():
    raw_email = "alice..smith@example.com"
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

@pytest.mark.parametrize(
        "raw_email", [
            "aliceexample.com",
            "alice@@example.com",
            "@example.com",
            "alice@.example.com"
        ]
)
def test_canonicalize_email_rejects_invalid_format(raw_email):
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

@pytest.mark.parametrize(
        "raw_email", [
            "สมชาย@example.com",
            "alice@ตัวอย่าง.com",
            "josé@example.com"
        ]
)
def test_canonicalize_email_rejects_non_ascii(raw_email):
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

def test_canonicalize_email_accepts_local_part_64_chars():
    local_part = "a" * 64
    raw_email = f"{local_part}@example.com"

    actual = canonicalize_email(raw_email)

    assert actual == raw_email

def test_canonicalize_email_rejects_local_part_65_chars():
    local_part = "a" * 65
    raw_email = f"{local_part}@example.com"

    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

def test_canonicalize_email_accepts_domain_label_63_chars():
    label = "a" * 63
    raw_email = f"alice@{label}.com"

    actual = canonicalize_email(raw_email)

    assert actual == raw_email

def test_canonicalize_email_rejects_domain_label_64_chars():
    label = "a" * 64
    raw_email = f"alice@{label}.com"

    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

def test_canonicalize_email_accepts_total_length_254_chars():
    local_part = "a" * 64

    domain = (
        f"{'b' * 63}."
        f"{'c' * 63}."
        f"{'d' * 57}.com"
    )

    raw_email = f"{local_part}@{domain}"

    assert len(raw_email) == 254

    actual = canonicalize_email(raw_email)

    assert actual == raw_email

def test_canonicalize_email_rejects_total_length_255_chars():
    local_part = "a" * 64

    domain = (
        f"{'b' * 63}."
        f"{'c' * 63}."
        f"{'d' * 58}.com"
    )

    raw_email = f"{local_part}@{domain}"

    assert len(raw_email) == 255

    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

@pytest.mark.parametrize(
        "raw_email", [
            "alice@-example.com",
            "alice@example-.com",
            "alice@exa_mple.com",
            "alice@example!.com"
        ]
)
def test_canonicalize_email_rejects_invalid_domain(raw_email):
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

@pytest.mark.parametrize(
    "raw_email", [
        "alice smith@example.com",
        "alice@exa mple.com"
    ]
)
def test_canonicalize_email_rejects_internal_whitespace(raw_email):
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

@pytest.mark.parametrize(
    "raw_email", [
        ".alice@example.com",
        "alice.@example.com",
        "alice@example..com",
        "alice@example.com.",
        "alice,smith@example.com"
    ]
)
def test_canonicalize_email_rejects_additional_invalid_formats(raw_email):
    with pytest.raises(ValueError, match="Invalid email"):
        canonicalize_email(raw_email)

def test_canonicalize_email_accepts_custom_domain():
    raw_email = "Alice@Mail.My-Company.CO.TH"
    expected = "alice@mail.my-company.co.th"

    actual = canonicalize_email(raw_email)

    assert actual == expected

def test_invalid_email_raises_typed_exception():
    with pytest.raises(InvalidEmail):
        canonicalize_email("invalid-email")