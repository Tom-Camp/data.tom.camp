import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DeviceDataRead(BaseModel):
    id: uuid.UUID
    created_date: datetime
    data: dict[str, Any]
    device_id: uuid.UUID
