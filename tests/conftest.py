import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.models.device import Device, DeviceData

# ── 1. Patch the engine BEFORE importing anything from your app ──────────────
from app.utils import database
from app.utils.config import settings

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # async SQLite in-memory

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

database.engine = test_engine
database.AsyncSessionFactory = TestingSessionLocal


from app.main import app  # noqa: E402 - import after patching the engine
from app.utils.database import (  # noqa: E402 - import after patching the engine
    get_session as get_db,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def create_test_tables():
    """Create schema once for the whole test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client(create_test_tables):
    """Fresh TestClient per test with DB dependency overridden."""
    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def admin_headers():
    """Headers with a valid admin secret for authenticated endpoints."""
    yield {"X-Admin-Secret": settings.ADMIN_SECRET_KEY}


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def db_session():
    """Provides a database session for direct DB operations in tests."""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def default_devices(db_session: AsyncSession):
    """Create default devices for testing."""

    devices = [
        Device(
            name="Test Device 1",
            description="First test device",
            notes={"location": "lab", "status": "active"},
        ),
        Device(
            name="Test Device 2",
            description="Second test device",
            notes={"location": "office", "status": "inactive"},
        ),
        Device(name="Test Device 3", description="Third test device", notes={}),
    ]

    for device in devices:
        db_session.add(device)

    await db_session.commit()

    for device in devices:
        await db_session.refresh(device)

    yield devices


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def device_with_data(
    db_session: AsyncSession, client, admin_headers, default_devices
):
    device = Device(
        name="Device with Data",
        description="A device that has associated data entries",
        notes={"location": "lab", "status": "active"},
    )
    db_session.add(device)
    await db_session.commit()
    await db_session.refresh(device)

    data_entry = [
        DeviceData(
            device_id=device.id,
            data={"temperature": 22.5, "humidity": 60},
        ),
        DeviceData(
            device_id=device.id,
            data={"temperature": 30.1, "humidity": 70},
        ),
        DeviceData(
            device_id=device.id,
            data={"temperature": 20.1, "humidity": 80},
        ),
    ]
    for data in data_entry:
        db_session.add(data)
    await db_session.commit()
    for data in data_entry:
        await db_session.refresh(data)
    await db_session.refresh(device)

    yield device
