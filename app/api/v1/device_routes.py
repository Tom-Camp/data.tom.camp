from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.device_schema import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService
from app.utils.auth import require_admin
from app.utils.database import get_session

device_routes = APIRouter(prefix="/v1/devices")

_DEVICE_EXCLUDE = {"api_key", "created_date", "data"}


def get_device_service(session: AsyncSession = Depends(get_session)) -> DeviceService:
    return DeviceService(session=session)


@device_routes.post(
    "/",
    dependencies=[Depends(require_admin)],
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
)
async def device_create(
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

    return DeviceRead(**new_device.model_dump(exclude=_DEVICE_EXCLUDE))


@device_routes.get("/", response_model=list[DeviceRead], status_code=status.HTTP_200_OK)
async def devices_list(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=200),
    service: DeviceService = Depends(get_device_service),
) -> list[DeviceRead]:
    """
    Route to list all devices.

    :param service: DeviceService; services.device_service.DeviceService
    :param limit: The maximum number of devices to return; default is 10.
    :param skip: The number of devices to skip before starting to collect the result set; default is 0.
    :return: List of Device; device_models.Device
    """
    logger.info("Listing devices with limit: {} and skip: {}", limit, skip)
    db_devices = await service.list(skip=skip, limit=limit)
    return [
        DeviceRead(**device.model_dump(exclude=_DEVICE_EXCLUDE))
        for device in db_devices
    ]


@device_routes.get("/{device_id}", response_model=DeviceRead)
async def device_read(
    device_id: UUID,
    service: DeviceService = Depends(get_device_service),
) -> DeviceRead:
    """
    Route to get a device by its ID.

    :param device_id: The ID of the device to retrieve.
    :param service: DeviceService; services.device_service.DeviceService
    :return: Device; device_models.Device
    """
    logger.info("Getting device with id: {}", device_id)
    db_device = await service.read(device_id=device_id)
    return DeviceRead(**db_device.model_dump(exclude=_DEVICE_EXCLUDE))


@device_routes.put(
    "/{device_id}",
    dependencies=[Depends(require_admin)],
    response_model=DeviceRead,
    status_code=status.HTTP_200_OK,
)
async def device_update(
    device_id: UUID,
    device_in: DeviceUpdate,
    service: DeviceService = Depends(get_device_service),
) -> DeviceRead:
    """
    Route to update a device by its ID.

    :param device_id: The ID of the device to update.
    :param device_in: DeviceUpdate object; schemas.device_schema.DeviceUpdate
    :param service: DeviceService; services.device_service.DeviceService
    :return: Device; device_models.Device
    """
    logger.info("Updating device with id: {}", device_id)
    db_device = await service.update(device_id=device_id, device_update=device_in)
    return DeviceRead(**db_device.model_dump(exclude=_DEVICE_EXCLUDE))


@device_routes.delete(
    "/{device_id}",
    dependencies=[Depends(require_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def device_delete(
    device_id: UUID,
    service: DeviceService = Depends(get_device_service),
) -> None:
    """
    Route to delete a device by its ID.

    :param device_id: The ID of the device to delete.
    :param service: DeviceService; services.device_service.DeviceService
    """
    logger.info("Deleting device with id: {}", device_id)
    await service.delete(device_id=device_id)
    return None
