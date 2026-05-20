from _collections_abc import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from loguru import logger
import os
import asyncio

pg_url = f'postgresql+asyncpg://{os.getenv("PG_USER")}:{os.getenv("PG_PASS")}@{os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_DB")}'

logger.debug(f">> PG_URL: {pg_url}")

engine = create_async_engine(
    pg_url,
    pool_size=100,
    max_overflow=25,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

AsyncPostgresSession = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncPostgresSession() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise

def ordered_table_defs():
    from deliverx.database.notifications import Notifications

ordered_table_defs