from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.data_schema import DeviceDataCreate, DeviceDataRead
from app.services.data_service import DataService
from app.utils.database import get_session

data_routes = APIRouter(prefix="/v1/data")


def get_device_service(session: AsyncSession = Depends(get_session)) -> DataService:
    return DataService(session=session)


@data_routes.post("/", status_code=status.HTTP_201_CREATED)
async def data_create(
    data_in: DeviceDataCreate,
    service: DataService = Depends(get_device_service),
) -> dict[str, str]:
    """
    Route to create a new device data entry.
    :param data_in: DeviceDataCreate; schemas.data_schema.DeviceDataCreate
    :param service: DataService; services.data_service.DataService
    :return: A dictionary containing the status and ID of the created device data entry.
    """
    logger.info("Creating device data with input: {}", data_in)
    return await service.create(data_in=data_in)


@data_routes.get(
    "/{data_id}",
    response_model=DeviceDataRead,
    status_code=status.HTTP_200_OK,
)
async def data_read(
    data_id: str,
    service: DataService = Depends(get_device_service),
) -> DeviceDataRead:
    """
    Route to get a device data entry by its ID.
    :param data_id: The ID of the device data entry to retrieve.
    :param service: DataService; services.data_service.DataService
    :return: DeviceData; device_models.DeviceData
    """
    logger.info("Getting device data with id: {}", data_id)
    db_data = await service.read(data_id=data_id)

    if db_data is None:
        logger.warning("Device data with id {} not found", data_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device data not found",
        )

    return DeviceDataRead(**db_data.model_dump(exclude={"updated_date", "device"}))


@data_routes.get(
    "/device/{device_id}",
    response_model=list[DeviceDataRead],
    status_code=status.HTTP_200_OK,
)
async def data_list(
    device_id: str,
    skip: int = 0,
    limit: int = 50,
    service: DataService = Depends(get_device_service),
) -> list[DeviceDataRead]:
    """
    Route to list device data entries for a specific device.
    :param device_id: The ID of the device to list data for.
    :param skip: The number of entries to skip (for pagination).
    :param limit: The maximum number of entries to return (for pagination).
    :param service: DataService; services.data_service.DataService
    :return: A list of DeviceDataRead objects representing the device data entries.
    """
    logger.info(
        "Listing device data for device id: {}, skip: {}, limit: {}",
        device_id,
        skip,
        limit,
    )
    db_data_list = await service.list(device_id=device_id, skip=skip, limit=limit)

    return [
        DeviceDataRead(**db_data.model_dump(exclude={"updated_date", "device"}))
        for db_data in db_data_list
        if db_data is not None
    ]
