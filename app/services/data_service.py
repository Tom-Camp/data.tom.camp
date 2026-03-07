from datetime import datetime, timezone
from typing import Any, Literal, Sequence
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.exceptions import NotFoundError
from app.models.api_key import ApiKey
from app.models.device import Device, DeviceData


class DataService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self, data_in: dict[str, Any], api_key: ApiKey) -> dict[str, str]:
        """
        Create a new device data entry in the database.
        :param data_in: A dictionary containing the device data to create.
        :param api_key: The API key for authentication, obtained from the verify_api_key dependency
        :return: A dictionary containing the status and ID of the created device data entry.
        """
        device_data = DeviceData(data=data_in, device_id=api_key.device_id)
        self._db.add(device_data)

        api_key.last_used_at = datetime.now(timezone.utc)
        self._db.add(api_key)

        await self._db.commit()
        await self._db.refresh(device_data)

        logger.info(
            "Created device data {} for device id: {}",
            device_data.id,
            api_key.device_id,
        )
        return {"status": "ok", "id": str(device_data.id)}

    async def read(self, data_id: UUID) -> DeviceData:
        """
        Get a device data entry by its ID.
        :param data_id: The ID of the device data entry to retrieve.
        :return: DeviceData; device_models.DeviceData
        """
        db_data: DeviceData | None = await self._db.get(DeviceData, data_id)
        if db_data is None:
            raise NotFoundError(f"Device data {data_id} not found")
        return db_data

    async def list(
        self,
        device_id: UUID,
        skip: int = 0,
        limit: int = 50,
        order: Literal["asc", "desc"] = "desc",
    ) -> Sequence[DeviceData]:
        """
        Get a list of all data entries for a given device.
        :param device_id: The ID of the device to retrieve data for.
        :param skip: Skip this many entries before returning.
        :param limit: Return at most this many entries.
        :param order: The order to return the entries in, either "asc" or "desc". Default is "desc".
        :return: A list of DeviceData objects; devices.device_models.DeviceData
        """
        device = await self._db.get(Device, device_id)
        if not device:
            raise NotFoundError(f"Device {device_id} not found")

        statement = (
            select(DeviceData)
            .offset(skip)
            .limit(limit)
            .where(DeviceData.device_id == device_id)
            .order_by(
                DeviceData.created_date.desc()  # type: ignore[union-attr]
                if order == "desc"
                else DeviceData.created_date.asc()  # type: ignore[union-attr]
            )
        )
        result = await self._db.execute(statement)
        return result.scalars().all()
