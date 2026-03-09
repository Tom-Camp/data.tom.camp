"""
One-time migration script to import data from devices.json (MongoDB export)
into the new PostgreSQL schema.

Usage:
    uv run python migrate.py [--file devices.json] [--dry-run]
"""

import argparse
import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.api_key import ApiKey  # noqa: F401
from app.models.device import Device, DeviceData
from app.utils.config import settings


def parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


async def migrate(file: Path, dry_run: bool) -> None:
    raw = json.loads(file.read_text())

    engine = create_async_engine(settings.async_database_url, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        for device_doc in raw:
            device = Device(
                name=device_doc.get("device_id", "").title(),
                notes=device_doc.get("notes", {}),
                api_key=None,
                created_date=parse_dt(device_doc.get("created_date", None)),
            )
            session.add(device)

            records = [
                DeviceData(
                    id=uuid.uuid4(),
                    device_id=device.id,
                    data=record["data"],
                    created_date=parse_dt(record["created_date"]),
                    updated_date=parse_dt(record["created_date"]),
                )
                for record in device_doc["data"]
            ]
            for r in records:
                session.add(r)

            print(f"  {device.name}: {len(records)} records")

        if dry_run:
            print("\nDry run — rolling back.")
            await session.rollback()
        else:
            await session.commit()
            print("\nMigration complete.")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="devices.json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    asyncio.run(migrate(args.file, args.dry_run))
