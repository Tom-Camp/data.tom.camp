from datetime import datetime

from pydantic import BaseModel


class ApiKeyOut(BaseModel):
    id: str
    api_key: str


class ApiKeyInfo(BaseModel):
    id: str
    device_id: str
    created_date: datetime
    revoked: bool
