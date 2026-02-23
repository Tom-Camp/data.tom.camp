from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.utils.database import get_session

device_routes = APIRouter(prefix="/devices")


@device_routes.post("", response_model=Device)
async def create_device(device: Device, session: AsyncSession = Depends(get_session)):
    pass
