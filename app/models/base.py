import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )

    created_date: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "type_": sa.DateTime(timezone=True),
            "server_default": func.now(),
        },
        nullable=False,
    )

    updated_date: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "type_": sa.DateTime(timezone=True),
            "server_default": func.now(),
            "onupdate": func.now(),
        },
    )

    class Config:
        arbitrary_types_allowed = True
