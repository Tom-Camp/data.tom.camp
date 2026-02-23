from secrets import token_urlsafe
from typing import Any
import uuid

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

JSONType = JSON().with_variant(JSONB(), "postgresql")


class DeviceData(ModelBase, table=True):
    data: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )
    device_id: uuid.UUID = Field(foreign_key="device.id", nullable=False)
    device: "Device" = Relationship(back_populates="data")


class Device(ModelBase, table=True):

    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    api_key: str = Field(default_factory=lambda: token_urlsafe(32))
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )
    data: list["DeviceData"] = Relationship(back_populates="device")
