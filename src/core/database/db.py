from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config.settings import settings

postgres_url = settings.database_url  

engine = create_async_engine(
    postgres_url,
    echo=settings.DB_ECHO_LOG,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    poolclass=AsyncAdaptedQueuePool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
