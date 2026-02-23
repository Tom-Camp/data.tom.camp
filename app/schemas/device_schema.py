from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.device import Device, DeviceData
from app.schemas.api_key_schema import ApiKeyInfo

JSONType = JSON().with_variant(JSONB(), "postgresql")


class DeviceCreate(Device):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )


class DeviceUpdate(Device):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )


class DeviceRead(Device):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONType,
        nullable=False,
    )
    api_keys: list[ApiKeyInfo] = Field()


class DeviceDataCreate(DeviceData):
    pass
