import pytest

from pathlib import Path

from app.auth.domain.password import (
    normalize_password, 
    prepare_password
)

from app.auth.infrastructure.hibp import get_password_sha1, get_password_hash_parts
from app.auth.infrastructure.common_passwords import is_common_password, load_common_passwords

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

def test_is_common_password_rejects_exact_match():
    common_passwords = {"password123", "12345678"}
    result = is_common_password("password123", common_passwords)
    assert result is True

def test_is_common_password_accepts_non_blocklisted_password():
    common_passwords = {"password123", "12345678"}
    result = is_common_password("MyUniquePassword2026!", common_passwords)
    assert result is False

def test_is_common_password_preserves_case_sensitivity():
    common_passwords = {"password123"}
    result = is_common_password("Password123", common_passwords)
    assert result is False

def test_is_common_password_preserves_whitespace():
    common_passwords = {"password123"}
    result = is_common_password(" password123 ", common_passwords)
    assert result is False

def test_common_password_screening_after_nfc():
    common_passwords = {"Café1234"}
    raw_password = "Cafe\u03011234"
    normalize_password = prepare_password(raw_password)
    result = is_common_password(normalize_password, common_passwords)
    assert result is True

def test_is_common_password_does_not_modify_inputs():
    common_passwords = {"password123"}
    password = " Password123 "

    original_password = password
    original_blocklist = common_passwords.copy()

    is_common_password(password, common_passwords)

    assert password == original_password
    assert common_passwords == original_blocklist

def test_load_common_passwords_from_file():
    file_path = Path(__file__).parent / "fixtures" / "common_passwords.txt"

    result = load_common_passwords(file_path)

    assert result == {"password123", "12345678", "Café1234"}

def test_load_common_passwords_nomalizes_nfc(tmp_path):
    file_path = tmp_path / "common_passwords.txt"
    file_path.write_text("Cafe\u03011234\n", encoding="utf-8")

    result = load_common_passwords(file_path)

    assert result == {"Caf\u00e91234"}

def test_load_common_passwords_missing_file_fails_closed(tmp_path):
    file_path = tmp_path / "missing_passwords.txt"

    with pytest.raises(FileNotFoundError):
        load_common_passwords(file_path)

def test_load_common_passwords_rejects_empty_dataset(tmp_path):
    file_path = tmp_path / "common_passwords.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Common password dataset is empty"):
        load_common_passwords(file_path)

def test_load_common_passwords_rejects_blank_lines_only(tmp_path):
    file_path = tmp_path / "common_passwords.txt"
    file_path.write_text("\n\n\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Common password dataset is empty"):
        load_common_passwords(file_path)

def test_get_passowrd_sha1():
    result = get_password_sha1("password123")

    assert result == "CBFDAC6008F9CAB4083784CBD1874F76618D2A97"
    assert len(result) == 40

def test_get_password_hash_parts():
    prefix, suffix = get_password_hash_parts("password123")

    assert prefix == "CBFDA"
    assert suffix == "C6008F9CAB4083784CBD1874F76618D2A97"
    assert len(prefix) == 5
    assert len(suffix) == 35