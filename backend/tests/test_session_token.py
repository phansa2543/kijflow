from app.auth.infrastructure.session_token import generate_session_token, digest_session_token

def test_generate_session_token():
    token1 = generate_session_token()
    token2 = generate_session_token()

    assert token1 != token2

    assert isinstance(token1, str)
    assert isinstance(token2, str)

    assert token1
    assert token2

def test_digest_session_token_determinism():
    token = "test-session-token"

    digest1 = digest_session_token(token)
    digest2 = digest_session_token(token)

    assert digest1 == digest2
    assert isinstance(digest1, bytes)
    assert digest1 != token.encode("utf-8")
    assert digest2 != token.encode("utf-8")

def test_digest_session_token_length():
    token = generate_session_token()
    digest = digest_session_token(token)

    assert len(digest) == 32