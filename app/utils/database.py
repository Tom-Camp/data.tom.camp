from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.utils.config import settings

DATABASE_URL = settings.async_database_url

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:  # type: ignore[attr-defined]
        await conn.run_sync(SQLModel.metadata.create_all)


async def dispose_engine() -> None:
    """Dispose of the engine and close all connections."""
    await engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
