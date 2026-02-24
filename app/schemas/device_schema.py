import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

JSONType = JSON().with_variant(JSONB(), "postgresql")


class DeviceCreate(SQLModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )


class DeviceUpdate(SQLModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )


class DeviceRead(SQLModel):
    id: uuid.UUID
    updated_date: datetime
    name: str
    description: str | None = None
    notes: dict[str, Any]
