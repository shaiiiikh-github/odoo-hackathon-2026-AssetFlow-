from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings

settings = get_settings()

# A single engine per process — pool_size/max_overflow tuned via settings so
# staging/prod can size the pool without code changes.
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,          # avoids stale-connection errors after DB restarts / idle timeouts
    echo=settings.DEBUG,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,      # objects stay usable after commit (needed since we return DTOs post-commit)
    autoflush=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields one session per request, guarantees close.
    Transaction boundaries (commit/rollback) are owned by the Unit of Work,
    NOT by this function — this only manages the connection lifecycle.
    """
    async with AsyncSessionFactory() as session:
        yield session
