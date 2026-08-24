"""Async database connection using SQLAlchemy + asyncpg + pgvector."""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    """Dependency-injectable async session generator."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Test the database connection on startup."""
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1
    print("Database connection verified")
