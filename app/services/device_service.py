from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.device import Device
from app.schemas.device_schema import DeviceCreate


class DeviceService:

    def __init__(self, session: AsyncSession):
        self._db = session

    async def create(self, device: DeviceCreate) -> Device:
        """
        Create a new device in database.

        :param device: DeviceCreate object; devices.device_schemas.DeviceCreate
        :return: Device object; devices.device_models.Device
        """

        db_device = Device(**device.model_dump())

        self._db.add(db_device)
        await self._db.flush()
        logger.info("Created device {} with id: {}", db_device.name, db_device.id)

        return db_device

    async def get_device_by_id(self, device_id: int) -> Device | None:
        """
        Get a device by its ID.

        :param device_id: The ID of the device to retrieve.
        :return: Device object; devices.device_models.Device
        """

        db_device: Device | None = await self._db.get(Device, device_id)

        if db_device is None:
            logger.warning("Device with id {} not found", device_id)
            return None

        logger.info("Retrieved device {} with id: {}", db_device.name, db_device.id)
        return db_device

    async def get_device_by_key(self, api_key: str) -> Device | None:
        """
        Get a device by its API key.

        :param api_key: The API key of the device to retrieve.
        :return: Device object; devices.device_models.Device
        """

        statement = select(Device).where(Device.api_key == api_key)
        result = await self._db.execute(statement)
        db_device = result.scalars().first()

        if db_device is None:
            logger.warning("Device with id {} not found", api_key)
            return None

        logger.info("Retrieved device {} with id: {}", db_device.name, db_device.id)
        return db_device
