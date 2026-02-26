def test_generate_api_key():
    from app.utils.auth import generate_api_key

    token = generate_api_key()
    assert isinstance(token, str)
    assert len(token) > 0


def test_hash_api_key():
    from app.utils.auth import hash_api_key

    raw_key = "test_api_key"
    hashed = hash_api_key(raw_key)
    assert isinstance(hashed, str)
    assert len(hashed) == 64
