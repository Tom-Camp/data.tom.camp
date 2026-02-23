from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.device_schema import Device, DeviceCreate


class DeviceService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create_device(self, device: DeviceCreate) -> Device:
        """
        Create a new device in database.

        :param device: DeviceCreate object; devices.device_schemas.DeviceCreate
        :return: Device object; devices.device_models.Device
        """

        db_device = Device(**device.model_dump())

        self._db.add(db_device)
        await self._db.commit()
        await self._db.refresh(db_device)
        logger.info("Created device {} with id: {}", db_device.device_id, db_device.id)

        return db_device
