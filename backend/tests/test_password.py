from app.auth.password import normalize_password

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