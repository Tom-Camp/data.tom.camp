import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    notes: dict[str, Any] | None = None


class DeviceRead(BaseModel):
    id: uuid.UUID
    updated_date: datetime
    name: str
    description: str | None = None
    notes: dict[str, Any]
