import hashlib
import secrets

API_KEY_LEN = 40


def generate_api_key() -> str:
    return secrets.token_urlsafe(API_KEY_LEN)


def hash_api_key(raw: str, salt: str) -> str:
    return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()
