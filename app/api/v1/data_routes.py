from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.schemas.data_schema import DeviceDataRead
from app.services.data_service import DataService
from app.utils.auth import verify_api_key
from app.utils.database import get_session

data_routes = APIRouter(prefix="/v1/data")

_DATA_EXCLUDE = {"device"}


def get_data_service(session: AsyncSession = Depends(get_session)) -> DataService:
    return DataService(session=session)


@data_routes.post(
    "/", response_model=dict[str, str], status_code=status.HTTP_201_CREATED
)
async def data_create(
    data_in: dict[str, Any],
    api_key: ApiKey = Depends(verify_api_key),
    service: DataService = Depends(get_data_service),
) -> dict[str, str]:
    """
    Route to create a new device data entry.
    :param data_in: A dictionary containing the device data to create.
    :param api_key: The API key for authentication, obtained from the verify_api_key dependency.
    :param service: DataService; services.data_service.DataService
    :return: A dictionary containing the status and ID of the created device data entry.
    """
    logger.info("Creating device data for device id: {}", api_key.device_id)
    return await service.create(data_in=data_in, api_key=api_key)


@data_routes.get(
    "/device/{device_id}",
    response_model=list[DeviceDataRead],
)
async def data_list(
    device_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    order: Literal["asc", "desc"] = Query(default="desc"),
    service: DataService = Depends(get_data_service),
) -> list[DeviceDataRead]:
    """
    Route to list device data entries for a specific device.
    :param device_id: The ID of the device to list data for.
    :param skip: The number of entries to skip (for pagination).
    :param limit: The maximum number of entries to return (for pagination).
    :param order: Sort order for results by created_date; "asc" or "desc" (default).
    :param service: DataService; services.data_service.DataService
    :return: A list of DeviceDataRead objects representing the device data entries.
    """
    logger.info(
        "Listing device data for device id: {}, skip: {}, limit: {}, order: {}",
        device_id,
        skip,
        limit,
        order,
    )
    db_data_list = await service.list(
        device_id=device_id, skip=skip, limit=limit, order=order
    )

    return [
        DeviceDataRead(**db_data.model_dump(exclude=_DATA_EXCLUDE))
        for db_data in db_data_list
    ]


@data_routes.get("/{data_id}", response_model=DeviceDataRead)
async def data_read(
    data_id: UUID,
    service: DataService = Depends(get_data_service),
) -> DeviceDataRead:
    """
    Route to get a device data entry by its ID.
    :param data_id: The ID of the device data entry to retrieve.
    :param service: DataService; services.data_service.DataService
    :return: DeviceData; device_models.DeviceData
    """
    logger.info("Getting device data with id: {}", data_id)
    db_data = await service.read(data_id=data_id)
    return DeviceDataRead(**db_data.model_dump(exclude=_DATA_EXCLUDE))
