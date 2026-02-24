from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.api_key import ApiKey
from app.models.device import Device, DeviceData
from app.schemas.data_schema import DeviceDataCreate
from app.utils.auth import verify_api_key


class DataService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self, data_in: DeviceDataCreate) -> dict[str, str]:
        """
        Create a new device data entry in the database.
        :param data_in: DeviceDataCreate; schemas.data_schema.DeviceDataCreate
        :return: A dictionary containing the status and ID of the created device data entry.
        """
        device = await self._db.get(Device, data_in.device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown device",
            )

        statement = select(ApiKey).where(ApiKey.device_id == data_in.device_id)
        result = await self._db.execute(statement)
        api_key = result.scalar_one_or_none()

        if api_key.revoked or not verify_api_key(data_in.api_key, api_key.key_hash):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )

        device_data = DeviceData(**data_in.model_dump(exclude={"api_key"}))
        self._db.add(device_data)

        api_key.last_used_at = datetime.now()
        self._db.add(api_key)

        await self._db.commit()
        await self._db.refresh(device_data)

        return {"status": "ok", "id": str(device_data.id)}

    async def read(self, data_id: str) -> DeviceData | None:
        """
        Get a device data entry by its ID.
        :param data_id: The ID of the device data entry to retrieve.
        :return: DeviceData; device_models.DeviceData
        """
        return await self._db.get(DeviceData, data_id)

    async def list(
        self, device_id: str, skip: int = 0, limit: int = 50
    ) -> Sequence[DeviceData | None]:
        """
        Get a list of all data entries for a given device.
        :param device_id: The ID of the device to retrieve data for.
        :param skip: Skip this many entries before returning.
        :param limit: Return at most this many entries.
        :return: A list of DeviceData objects; devices.device_models.DeviceData
        """
        device = await self._db.get(Device, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown device",
            )
        statement = (
            select(DeviceData)
            .offset(skip)
            .limit(limit)
            .where(DeviceData.device_id == device_id)
        )
        result = await self._db.execute(statement)
        data = result.scalars().all()
        return data
