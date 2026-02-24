from fastapi import HTTPException
from loguru import logger
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

        :param device_key: The API key to create.
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

    async def delete(self, key_id: str) -> None:
        """
        Delete an API key by its ID.

        :param key_id: The ID of the API key to delete.
        """
        db_api_key: ApiKey | None = await self._db.get(ApiKey, key_id)
        if not db_api_key:
            logger.warning("API key with id {} not found", key_id)
            raise HTTPException(status_code=404, detail="Not found")

        await self._db.delete(db_api_key)
        await self._db.commit()
        logger.info("Deleted API key with id: {}", key_id)
