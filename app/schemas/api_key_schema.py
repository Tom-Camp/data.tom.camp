import uuid
from datetime import datetime

from sqlmodel import SQLModel


class ApiKeyCreate(SQLModel):
    device_id: uuid.UUID
    key_hash: str


class ApiKeyOut(SQLModel):
    id: uuid.UUID
    api_key: str


class ApiKeyInfo(SQLModel):
    id: str
    device_id: str
    created_date: datetime
    revoked: bool


class ApiKeyUpdate(SQLModel):
    revoked: bool
