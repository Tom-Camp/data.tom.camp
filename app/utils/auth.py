import hashlib
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.services.api_key_service import ApiKeyService
from app.utils.config import settings
from app.utils.database import get_session

API_KEY_LEN = 40


def get_api_key_service(session: AsyncSession = Depends(get_session)) -> ApiKeyService:
    return ApiKeyService(session=session)


def require_admin(x_admin_secret: str | None = Header(None)):
    if not x_admin_secret or not secrets.compare_digest(
        x_admin_secret, settings.ADMIN_SECRET_KEY
    ):
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


async def verify_api_key(
    raw_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    device_id: Annotated[UUID | None, Header(alias="X-Device-Id")] = None,
    api_service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKey:
    if raw_key is None or device_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication headers",
        )
    api_key = await api_service.get_api_key(device_id=device_id)

    if not hash_api_key(raw_key) == api_key.key_hash or api_key.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key
