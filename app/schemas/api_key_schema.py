import uuid

from sqlmodel import SQLModel


class ApiKeyCreate(SQLModel):
    device_id: uuid.UUID
    key_hash: str


class ApiKeyOut(SQLModel):
    id: uuid.UUID
    api_key: str
