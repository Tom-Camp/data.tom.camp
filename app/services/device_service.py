import uuid
from typing import Sequence

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.device import Device
from app.schemas.device_schema import DeviceCreate, DeviceUpdate


class DeviceService:

    def __init__(self, session: AsyncSession):
        self._db = session

    @staticmethod
    def _normalize_device_id(device_id: str | uuid.UUID) -> uuid.UUID:
        if isinstance(device_id, uuid.UUID):
            return device_id
        return uuid.UUID(device_id)

    async def create(self, device_create: DeviceCreate) -> Device:
        """
        Create a new device in database.

        :param device_create: DeviceCreate object; devices.device_schemas.DeviceCreate
        :return: Device object; devices.device_models.Device
        """

        db_device = Device(**device_create.model_dump())

        self._db.add(db_device)
        await self._db.commit()
        await self._db.refresh(db_device)
        logger.info("Created device {} with id: {}", db_device.name, db_device.id)

        return db_device

    async def read(self, device_id: str | uuid.UUID) -> Device | None:
        """
        Get a device by its ID.

        :param device_id: The ID of the device to retrieve.
        :return: Device object; devices.device_models.Device
        """

        db_device: Device | None = await self._db.get(
            Device,
            self._normalize_device_id(device_id),
        )
        if db_device is None:
            logger.warning("Device with id {} not found", device_id)
            return None
        return db_device

    async def update(
        self,
        device_id: str | uuid.UUID,
        device_update: DeviceUpdate,
    ) -> Device:
        """
        Update a device by its ID.

        :param device_id: The ID of the device to update.
        :param device_update: DeviceUpdate object; devices.device_schemas.DeviceUpdate
        :return: Updated Device object; devices.device_models.Device
        """

        db_device: Device | None = await self._db.get(
            Device,
            self._normalize_device_id(device_id),
        )
        if db_device is None:
            logger.warning("Device with id {} not found", device_id)
            raise HTTPException(status_code=404, detail="Not found")

        for key, value in device_update.model_dump(exclude_unset=True).items():
            setattr(db_device, key, value)

        self._db.add(db_device)
        await self._db.commit()
        await self._db.refresh(db_device)
        logger.info("Updated device {} with id: {}", db_device.name, db_device.id)

        return db_device

    async def delete(self, device_id: str | uuid.UUID) -> None:
        """
        Delete a device by its ID.

        :param device_id: The ID of the device to delete.
        """

        db_device: Device | None = await self._db.get(
            Device,
            self._normalize_device_id(device_id),
        )
        if db_device is None:
            logger.warning("Device with id {} not found", device_id)
            raise HTTPException(status_code=404, detail="Not found")

        await self._db.delete(db_device)
        await self._db.commit()
        logger.info("Deleted device {} with id: {}", db_device.name, db_device.id)

    async def list(self, skip: int = 0, limit: int = 50) -> Sequence[Device | None]:
        """
        List devices with pagination.

        :param skip: Number of records to skip for pagination.
        :param limit: Maximum number of records to return for pagination.
        :return:
        """

        statement = select(Device).offset(skip).limit(limit)
        result = await self._db.execute(statement)
        devices = result.scalars().all()
        return devices
