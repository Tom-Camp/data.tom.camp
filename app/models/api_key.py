import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.device import Device  # noqa: F401


class ApiKey(ModelBase, table=True):  # type: ignore
    key_hash: str = Field(nullable=False, unique=True)
    revoked: bool = Field(default=False)
    last_used_at: datetime | None = Field(default=None)
    device_id: uuid.UUID = Field(foreign_key="device.id", nullable=False)
    device: "Device" = Relationship(back_populates="api_key")
