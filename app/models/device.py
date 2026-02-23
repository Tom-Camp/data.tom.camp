from secrets import token_urlsafe
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import BaseModel

JSONType = JSON().with_variant(JSONB(), "postgresql")


class DeviceData(BaseModel):
    data: dict[str, Any] = Field(
        sa_column_kwargs={"type_": JSONType},
        nullable=False,
    )


class Device(BaseModel):
    device_id: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    api_key: str = Field(default_factory=lambda: token_urlsafe(32))
    notes: dict = {}
    data: list[DeviceData] = []
