import uuid
from datetime import datetime
from typing import Any

from sqlmodel import SQLModel


class DeviceDataCreate(SQLModel):
    data: dict[str, Any]
    device_id: str
    api_key: str


class DeviceDataRead(SQLModel):
    id: uuid.UUID
    created_date: datetime
    data: dict[str, Any]
    device_id: uuid.UUID
