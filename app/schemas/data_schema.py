import uuid
from datetime import datetime
from typing import Any

from sqlmodel import SQLModel


class DeviceDataRead(SQLModel):
    id: uuid.UUID
    created_date: datetime
    data: dict[str, Any]
    device_id: uuid.UUID
