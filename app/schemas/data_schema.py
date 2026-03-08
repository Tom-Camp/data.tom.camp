from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class DeviceDataRead(BaseModel):
    id: UUID
    created_date: datetime
    updated_date: datetime
    data: dict[str, Any]
    device_id: UUID
