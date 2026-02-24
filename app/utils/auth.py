import hashlib
import secrets

from fastapi import Header, HTTPException
from loguru import logger

from app.utils.config import settings

API_KEY_LEN = 40


def require_admin(x_admin_secret: str = Header(...)):
    logger.debug("x_admin_secret: {}", x_admin_secret)
    if not secrets.compare_digest(x_admin_secret, settings.ADMIN_SECRET_KEY):
        raise HTTPException(status_code=403)


def generate_api_key() -> str:
    return secrets.token_urlsafe(API_KEY_LEN)


def hash_api_key(raw: str) -> str:
    """
    Hash an API key using SHA-256 with a salt.

    :param raw: The raw API key to hash.
    :return:
    """
    return hashlib.sha256((settings.HASH_SALT + raw).encode("utf-8")).hexdigest()


def verify_api_key(raw: str, hashed: str) -> bool:
    """
    Verify a raw API key against a hashed value.

    :param raw: The raw API key to verify.
    :param hashed: The hashed API key to compare against.
    :return: True if the raw API key matches the hashed value, False otherwise.
    """
    return hash_api_key(raw) == hashed
