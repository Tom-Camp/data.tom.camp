import uuid

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    device_id: uuid.UUID
    key_hash: str


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    api_key: str
