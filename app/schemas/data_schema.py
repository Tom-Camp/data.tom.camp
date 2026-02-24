from typing import Any

from sqlmodel import SQLModel


class DeviceDataCreate(SQLModel):
    data: dict[str, Any]
    device_id: str


class DeviceDataRead(SQLModel):
    id: str
    data: dict[str, Any]
    device_id: str
    created_date: str
