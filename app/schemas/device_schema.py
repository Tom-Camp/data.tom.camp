import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel


class DeviceCreate(SQLModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(SQLModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    notes: dict[str, Any] = Field(default_factory=dict)


class DeviceRead(SQLModel):
    id: uuid.UUID
    updated_date: datetime
    name: str
    description: str | None = None
    notes: dict[str, Any]
    api_key: uuid.UUID | None = None
