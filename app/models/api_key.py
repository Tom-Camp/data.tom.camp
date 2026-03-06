import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.device import Device  # noqa: F401


class ApiKey(ModelBase, table=True):  # type: ignore
    key_hash: str = Field(
        sa_column=sa.Column(sa.String(64), nullable=False, unique=True)
    )
    revoked: bool = Field(
        default=False, sa_column_kwargs={"server_default": sa.false()}
    )
    last_used_at: datetime | None = Field(
        default=None, sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )
    device_id: uuid.UUID = Field(foreign_key="device.id", unique=True)
    device: "Device" = Relationship(back_populates="api_key")
