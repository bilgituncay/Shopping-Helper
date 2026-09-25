from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from shared.config import settings

# Sync engine: used by the Clery worker

sync_engine = create_engine(settings.database_url, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async engine: used by FastAPI

async_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session