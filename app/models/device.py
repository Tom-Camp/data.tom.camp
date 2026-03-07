import uuid
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.api_key import ApiKey  # noqa: F401

JSONType = JSON().with_variant(JSONB(), "postgresql")


class Device(ModelBase, table=True):  # type: ignore
    name: str = Field(..., max_length=255, unique=True)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=sa.Column(JSONType, nullable=False),
    )
    api_key: "ApiKey | None" = Relationship(back_populates="device")
    data: list["DeviceData"] = Relationship(back_populates="device")


class DeviceData(ModelBase, table=True):  # type: ignore
    data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=sa.Column(JSONType, nullable=False),
    )
    device_id: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.Uuid,
            sa.ForeignKey("device.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    device: "Device" = Relationship(back_populates="data")
