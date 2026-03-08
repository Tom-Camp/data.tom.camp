from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class DeviceCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    notes: dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    notes: dict[str, Any] | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "DeviceUpdate":
        if all(v is None for v in (self.name, self.description, self.notes)):
            raise ValueError("At least one field must be provided")
        return self


class DeviceRead(BaseModel):
    id: UUID
    created_date: datetime
    updated_date: datetime
    name: str
    description: str | None = None
    notes: dict[str, Any]
