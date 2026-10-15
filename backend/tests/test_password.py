import pytest

from app.auth.password import normalize_password, prepare_password

def test_normalize_password_preserves_whitespace():
    raw_password = "  Hello Word  "
    result = normalize_password(raw_password)
    assert result == raw_password

def test_normalize_password_unicode_nfc_equivalence():
    precomposed = "\u00E9"
    decomposed = "e\u0301"

    result_precomposed = normalize_password(precomposed)
    result_decomposed = normalize_password(decomposed)

    assert result_precomposed == result_decomposed
    assert result_decomposed == "\u00E9"

def test_normalize_password_preserves_case():
    raw_password = "HelloWORLD"

    result = normalize_password(raw_password)

    assert result == "HelloWORLD"
    assert result != "helloworld"

def test_normalize_password_preserves_thai_characters():
    raw_password = "รหัสผ่านภาษาไทย123"

    result = normalize_password(raw_password)

    assert result == raw_password

def test_normalize_password_is_idempotent():
    raw_password = "Cafe\u0301 Password"

    first_result = normalize_password(raw_password)
    second_result = normalize_password(first_result)

    assert second_result == first_result
    assert first_result == "Café Password"

def test_prepare_password_rejects_below_minimum_length():
    raw_password = "a" * 7

    with pytest.raises(ValueError, match="Password is too short"):
        prepare_password(raw_password)

def test_prepare_password_accepts_minimum_length():
    raw_password = "a" * 8

    actual = prepare_password(raw_password)

    assert actual == raw_password

def test_prepare_password_accepts_above_minimum_length():
    raw_password = "a" * 9

    actual = prepare_password(raw_password)

    assert actual == raw_password

def test_prepare_password_accepts_maximum_length():
    raw_password = "a" * 128

    actual = prepare_password(raw_password)

    assert actual == raw_password

def test_prepare_password_rejects_above_maximum_length():
    raw_password = "a" * 129

    with pytest.raises(ValueError, match="Password is too long"):
        prepare_password(raw_password)

def test_prepare_password_validates_length_after_nfc():
    raw_password = "a" * 7 + "e\u0301"

    result = prepare_password(raw_password)

    assert result == "a" * 7 + "\u00e9"
    assert len(result) == 8

def test_prepare_password_rejects_below_minimum_after_nfc():
    raw_password = "a" * 6 + "e\u0301"

    with pytest.raises(ValueError, match="Password is too short"):
        prepare_password(raw_password)

def test_prepare_password_preserves_whitespace():
    raw_password = "  abcd  "
    result = prepare_password(raw_password)

    assert result == raw_password
    assert len(result) == 8

def test_prepare_password_preserves_case():
    raw_password = "HelloWORLD"
    result = prepare_password(raw_password)

    assert result == raw_password
    assert result != "helloworld"

def test_prepare_password_accepts_thai_characters():
    raw_password = "รหัสผ่าน123"
    result = prepare_password(raw_password)

    assert result == raw_password
    assert 8 <= len(result) <= 128

def test_prepare_password_never_truncates():
    raw_password = "a" * 200

    with pytest.raises(ValueError, match="Password is too long"):
        prepare_password(raw_password)