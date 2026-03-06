import hashlib
import re

from app.utils.auth import API_KEY_LEN, generate_api_key, hash_api_key
from app.utils.config import settings


def test_generate_api_key():
    token = generate_api_key()
    assert isinstance(token, str)
    assert len(token) >= API_KEY_LEN
    assert re.match(r"^[A-Za-z0-9_-]+$", token), "Key should be URL-safe"


def test_hash_api_key():
    raw_key = "test_api_key"
    hashed = hash_api_key(raw_key)
    assert isinstance(hashed, str)

    expected_len = len(hashlib.new(settings.HASH_ALGORITHM, b"").hexdigest())
    assert len(hashed) == expected_len


def test_hash_api_key_is_deterministic():
    raw_key = "test_api_key"
    assert hash_api_key(raw_key) == hash_api_key(raw_key)


def test_hash_api_key_differs_for_different_inputs():
    assert hash_api_key("key_one") != hash_api_key("key_two")
