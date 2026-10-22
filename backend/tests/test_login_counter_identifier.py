import hashlib, hmac, pytest

from app.auth.infrastructure.login_counter_identifier import (
    make_account_counter_identifier,
    load_login_counter_hmac_secret
)


TEST_SECRET = bytes(range(32))


def test_account_identifier_is_deterministic():
    first = make_account_counter_identifier(
        "user@example.com",
        TEST_SECRET,
    )
    second = make_account_counter_identifier(
        "user@example.com",
        TEST_SECRET,
    )

    assert first == second
    assert len(first) == 64
    assert first != "user@example.com"


def test_account_identifier_uses_hmac_sha256():
    email = "user@example.com"

    expected = hmac.new(
        TEST_SECRET,
        email.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    actual = make_account_counter_identifier(email, TEST_SECRET)

    assert actual == expected


def test_account_identifier_changes_with_secret():
    first = make_account_counter_identifier(
        "user@example.com",
        TEST_SECRET,
    )
    second = make_account_counter_identifier(
        "user@example.com",
        bytes(range(1, 33)),
    )

    assert first != second


@pytest.mark.parametrize(
    "email, secret",
    [
        ("", TEST_SECRET),
        ("user@example.com", b"short"),
    ],
)
def test_account_identifier_rejects_invalid_inputs(email, secret):
    with pytest.raises(ValueError):
        make_account_counter_identifier(email, secret)

def test_load_login_counter_hmac_secret_valid(monkeypatch):
    expected = bytes(range(32))
    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", expected.hex())

    assert load_login_counter_hmac_secret() == expected


def test_load_login_counter_hmac_secret_missing(monkeypatch):
    monkeypatch.delenv("LOGIN_COUNTER_HMAC_SECRET", raising=False)

    with pytest.raises(ValueError):
        load_login_counter_hmac_secret()


@pytest.mark.parametrize(
    "invalid_secret",
    [
        "short",
        "z" * 64,
        "00" * 31,
        "00" * 33,
    ],
)
def test_load_login_counter_hmac_secret_invalid(
    monkeypatch, invalid_secret
):
    monkeypatch.setenv("LOGIN_COUNTER_HMAC_SECRET", invalid_secret)

    with pytest.raises(ValueError):
        load_login_counter_hmac_secret()