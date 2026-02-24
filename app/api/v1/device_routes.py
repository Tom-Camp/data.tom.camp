from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.device_schema import DeviceCreate, DeviceRead
from app.services.device_service import DeviceService
from app.utils.auth import require_admin
from app.utils.database import get_session

device_routes = APIRouter(prefix="/v1/devices")


def get_device_service(session: AsyncSession = Depends(get_session)) -> DeviceService:
    return DeviceService(session=session)


@device_routes.post(
    "/",
    dependencies=[Depends(require_admin)],
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    device_in: DeviceCreate,
    service: DeviceService = Depends(get_device_service),
) -> DeviceRead:
    """
    Route to create a new device.

    :param device_in: DeviceCreate object; schemas.device_schema.DeviceCreate
    :param service: DeviceService; services.device_service.DeviceService
    :return: Device; device_models.Device
    """
    logger.info("Creating device with name: {}", device_in.name)
    new_device = await service.create(device_create=device_in)

    return DeviceRead(
        **new_device.model_dump(exclude={"api_key", "created_date", "data"})
    )


@device_routes.get("/", response_model=list[DeviceRead], status_code=status.HTTP_200_OK)
async def list_devices(
    limit: int = 10,
    offset: int = 0,
    service: DeviceService = Depends(get_device_service),
) -> list[DeviceRead]:
    """
    Route to list all devices.

    :param service: DeviceService; services.device_service.DeviceService
    :param limit: The maximum number of devices to return; default is 10.
    :param offset: The number of devices to skip before starting to collect the result set; default is 0.
    :return: List of Device; device_models.Device
    """

    db_devices = await service.list(skip=offset, limit=limit)
    logger.info("Listing devices with limit: {} and offset: {}", limit, offset)
    return [
        DeviceRead(**device.model_dump(exclude={"api_key", "created_date", "data"}))
        for device in db_devices
        if device is not None
    ]


@device_routes.get(
    "/{device_id}", response_model=DeviceRead, status_code=status.HTTP_200_OK
)
async def get_device(
    device_id: str,
    service: DeviceService = Depends(get_device_service),
) -> DeviceRead:
    """
    Route to get a device by its ID.

    :param device_id: The ID of the device to retrieve.
    :param service: DeviceService; services.device_service.DeviceService
    :return: Device; device_models.Device
    """
    logger.info("Getting device with id: {}", device_id)
    db_device = await service.get(device_id=device_id)

    if db_device is None:
        logger.warning("Device with id {} not found", device_id)
        raise HTTPException(status_code=404, detail="Not found")

    return DeviceRead(
        **db_device.model_dump(exclude={"api_key", "created_date", "data"})
    )
