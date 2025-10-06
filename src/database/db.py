from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from contextlib import asynccontextmanager
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class DatabaseManager:
    """Manages async database connections and sessions."""
    
    def __init__(self):
        self._engine = None
        self._session_factory = None
        self._settings = get_settings()
    
    def get_engine(self):
        """Get or create the async database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self._settings.database_url,
                echo=False,  # Set to True for SQL query logging
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            logger.info("Database engine created")
        return self._engine
    
    def get_session_factory(self):
        """Get or create the async session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.info("Session factory created")
        return self._session_factory
    
    async def close(self):
        """Close the database engine."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")


# Global database manager instance
db_manager = DatabaseManager()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get an async database session.
    
    Usage:
        async def some_function():
            async for session in get_async_session():
                # Use session here
                result = await session.execute(select(SomeModel))
                # Session will be automatically closed
    """
    session_factory = db_manager.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncSession:
    """
    Context manager to get an async database session.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(select(SomeModel))
            # Session will be automatically committed and closed
    """
    session_factory = db_manager.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables():
    """Create all database tables."""
    engine = db_manager.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_tables():
    """Drop all database tables."""
    engine = db_manager.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")


async def close_db():
    """Close database connections."""
    await db_manager.close()