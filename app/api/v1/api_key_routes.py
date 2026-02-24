from fastapi import APIRouter, Depends, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.schemas.api_key_schema import ApiKeyOut
from app.services.api_key_service import ApiKeyService
from app.utils.auth import generate_api_key, hash_api_key, require_admin
from app.utils.database import get_session

api_key_routes = APIRouter(prefix="/v1/keys")


def get_api_key_service(session: AsyncSession = Depends(get_session)) -> ApiKeyService:
    return ApiKeyService(session=session)


@api_key_routes.post(
    "/{device_id}",
    dependencies=[Depends(require_admin)],
    response_model=ApiKeyOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    device_id: int,
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKeyOut:
    """
    Route to create a new API key for a device.

    :param device_id: The ID of the device to create the API key for.
    :param service: ApiKeyService; services.api_key_service.ApiKeyService
    :return: The raw API key string.
    """
    logger.info("Creating API key for device ID: {}", device_id)

    raw_key = generate_api_key()
    key_id = raw_key[:10]
    key_hash = hash_api_key(raw_key)

    api_key = await service.create(
        api_key=ApiKey(
            key_id=key_id,
            key_hash=key_hash,
            device_id=device_id,
        )
    )

    return ApiKeyOut(id=api_key.id, api_key=raw_key)
