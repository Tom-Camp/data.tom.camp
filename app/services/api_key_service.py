from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.api_key import ApiKey
from app.models.device import Device
from app.schemas.api_key_schema import ApiKeyCreate


class ApiKeyService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self, device_key: ApiKeyCreate) -> ApiKey:
        """
        Create a new API key in database.

        :param device_key: ApiKeyCreate object; schemas.api_key_schema.ApiKeyCreate
        :return: ApiKey
        """
        db_device: Device | None = await self._db.get(Device, device_key.device_id)
        if not db_device:
            logger.warning("Device with id {} not found", device_key.device_id)
            raise NotFoundError(f"Device {device_key.device_id} not found")

        existing = await self._db.execute(
            select(ApiKey).where(ApiKey.device_id == device_key.device_id)
        )
        if existing.scalars().one_or_none() is not None:
            raise ConflictError(f"Device {device_key.device_id} already has an API key")

        db_api_key = ApiKey(**device_key.model_dump())
        self._db.add(db_api_key)
        await self._db.commit()
        await self._db.refresh(db_api_key)
        logger.info("Created API key: {}", db_api_key.id)

        return db_api_key

    async def get_api_key(self, device_id: UUID) -> ApiKey:
        """
        Get an API key by device ID.

        :param device_id: The ID of the device to retrieve the API key for.
        :return: ApiKey object; models.api_key.ApiKey
        """
        statement = select(ApiKey).where(ApiKey.device_id == device_id)
        result = await self._db.execute(statement)
        key = result.scalars().one_or_none()

        if not key:
            logger.warning("API key for device id {} not found", device_id)
            raise NotFoundError(f"API key for device {device_id} not found")

        return key

    async def revoke(self, device_id: UUID) -> None:
        """
        Revoke an API key by device ID.
        :param device_id: The ID of the device whose API key should be revoked.
        """
        api_key = await self.get_api_key(device_id=device_id)
        api_key.revoked = True
        self._db.add(api_key)
        await self._db.commit()
        logger.info("Revoked API key with id: {}", api_key.id)

    async def refresh(self, key_hash: str, device_id: UUID) -> UUID:
        """
        Replace the API key hash for a device with a new one.
        :param key_hash: The new API key hash.
        :param device_id: The ID of the device to retrieve the API key for.
        :return: The ID of the updated ApiKey.
        """
        api_key = await self.get_api_key(device_id=device_id)
        api_key.key_hash = key_hash
        self._db.add(api_key)
        await self._db.commit()
        await self._db.refresh(api_key)

        logger.info("Refreshed API key for device id: {}", api_key.device_id)
        return api_key.id
