from fastapi import APIRouter, Depends, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import ApiKey
from app.schemas.device_schema import DeviceCreate, DeviceReadWithKey
from app.services.device_service import DeviceService
from app.utils.auth import generate_api_key, hash_api_key, require_admin
from app.utils.database import get_session

device_routes = APIRouter(prefix="/devices")


def get_bed_service(session: AsyncSession = Depends(get_session)) -> DeviceService:
    return DeviceService(session=session)


@device_routes.post(
    "",
    dependencies=[Depends(require_admin)],
    response_model=DeviceReadWithKey,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    device_in: DeviceCreate,
    service: DeviceService = Depends(get_bed_service),
) -> DeviceReadWithKey:
    """
    Route to create a new device.

    :param device_in: DeviceCreate object; schemas.device_schema.DeviceCreate
    :param service: DeviceService; services.device_service.DeviceService
    :return: Device; device_models.Device
    """
    logger.info("Creating device with name: {}", device_in.name)
    new_device = await service.create(device=device_in)

    raw_key = generate_api_key()
    key_id = raw_key[:10]
    key_hash = hash_api_key(raw_key)

    api_key = ApiKey(
        key_id=key_id,
        key_hash=key_hash,
        device_id=new_device.id,
    )
    service._db.add(api_key)
    await service._db.commit()
    await service._db.refresh(new_device)

    return DeviceReadWithKey(
        id=new_device.id,
        name=new_device.name,
        description=new_device.description,
        notes=new_device.notes,
        api_key=raw_key,
        key_id=key_id,
    )
