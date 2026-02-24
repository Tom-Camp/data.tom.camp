from datetime import datetime

from sqlmodel import SQLModel


class ApiKeyOut(SQLModel):
    id: str
    api_key: str


class ApiKeyInfo(SQLModel):
    id: str
    device_id: str
    created_date: datetime
    revoked: bool
