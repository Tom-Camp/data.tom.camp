from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
            raise HTTPException(status_code=404, detail="Not found")

        db_api_key = ApiKey(**device_key.model_dump())
        self._db.add(db_api_key)
        await self._db.commit()
        await self._db.refresh(db_api_key)
        logger.info("Created API key: {}", db_api_key.id)

        return db_api_key

    async def revoke(self, device_id: str) -> dict[str, str]:
        """
        Revoke an API key by its ID.
        :param device_id: The ID of the device whose API key should be revoked.
        :return: A dictionary with a message confirming the revocation.
        """
        statement = select(ApiKey).where(ApiKey.device_id == device_id)
        result = await self._db.execute(statement)
        key_data = result.scalars().one_or_none()
        if not key_data:
            logger.warning("API key for device id {} not found", device_id)
            raise HTTPException(status_code=404, detail="Not found")

        key_data.revoked = True
        self._db.add(key_data)
        await self._db.commit()
        logger.info("Revoked API key with id: {}", key_data.id)
        return {"message": f"API key with id {key_data.id} has been revoked."}

    async def refresh(self, key_data: ApiKeyCreate) -> ApiKey:
        """
        Refresh an API key for a device by revoking the old key and creating a new one.

        :param key_data: ApiKeyCreate object; schemas.api_key_schema.ApiKeyCreate
        :return: The new ApiKey object.
        """
        statement = select(ApiKey).where(ApiKey.device_id == key_data.device_id)
        result = await self._db.execute(statement)
        key_data = result.scalars().one_or_none()
        if not key_data:
            logger.warning("API key for device id {} not found", key_data.device_id)
            raise HTTPException(status_code=404, detail="Not found")

        key_data.key_hash = key_data.key_hash
        key_data.revoked = False
        self._db.add(key_data)
        await self._db.commit()
        await self._db.refresh(key_data)
        logger.info("Refreshed API key for device id: {}", key_data.device_id)
        return key_data
