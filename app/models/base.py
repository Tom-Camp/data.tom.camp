import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy import func
from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    created_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),  # type: ignore[arg-type]
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )

    updated_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),  # type: ignore[arg-type]
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
        nullable=False,
    )
