from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from .config import settings

# Convert postgresql:// to postgresql+asyncpg:// for async
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Async Database engine
async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug  # SQL logging in debug mode
)

# Sync engine for table creation and migrations
sync_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Async Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_async_db():
    """Async database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_db():
    """Sync database session dependency (for migrations only)"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
