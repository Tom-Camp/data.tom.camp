from uuid import UUID

from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    device_id: UUID
    key_hash: str


class ApiKeyOut(BaseModel):
    id: UUID
    api_key: str
