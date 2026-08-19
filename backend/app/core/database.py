"""SQLAlchemy async engine and session factory for SQLite."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=(settings.app_env == "development"),
)

sync_database_url = settings.database_url.replace("+aiosqlite", "")
sync_engine = create_engine(sync_database_url, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def init_db():
    """Create all tables."""
    from app.models import device, spray_event  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_sync_db():
    """Create tables for synchronous controller transactions."""
    from app.models import device, spray_event  # noqa: F401

    Base.metadata.create_all(sync_engine)


async def get_db() -> AsyncSession:
    """Dependency that provides a database session."""
    async with async_session() as session:
        yield session
