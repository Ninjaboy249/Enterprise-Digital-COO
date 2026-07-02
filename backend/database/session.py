"""
Database Session Management
Provides async SQLAlchemy session management with connection pooling
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event, text
import logging

from config import settings

logger = logging.getLogger(__name__)

# Base class for all ORM models
Base = declarative_base()

# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker] = None


def get_database_url() -> str:
    """
    Construct database URL from settings
    
    Returns:
        Database connection URL
    """
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def create_engine(
    url: Optional[str] = None,
    echo: bool = False,
    pool_size: int = 20,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    pool_recycle: int = 3600,
) -> AsyncEngine:
    """
    Create async SQLAlchemy engine with connection pooling
    
    Args:
        url: Database URL (uses settings if not provided)
        echo: Enable SQL query logging
        pool_size: Number of connections to maintain
        max_overflow: Max connections beyond pool_size
        pool_pre_ping: Test connections before use
        pool_recycle: Recycle connections after N seconds
        
    Returns:
        Configured AsyncEngine
    """
    if url is None:
        url = get_database_url()
    
    # Create engine with connection pooling
    engine = create_async_engine(
        url,
        echo=echo or settings.DEBUG,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        pool_recycle=pool_recycle,
        # Connection arguments
        connect_args={
            "host": settings.POSTGRES_HOST,  # Pass host directly to avoid DNS issues
            "port": settings.POSTGRES_PORT,
            "user": settings.POSTGRES_USER,
            "password": settings.POSTGRES_PASSWORD,
            "database": settings.POSTGRES_DB,
            "server_settings": {
                "application_name": "enterprise_coo",
                "jit": "off",  # Disable JIT for faster simple queries
            },
            "command_timeout": 60,
            "timeout": 10,
            "ssl": False,  # Disable SSL to avoid DNS resolution issues on Windows
        },
    )
    
    # Register event listeners
    @event.listens_for(engine.sync_engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Set connection parameters on new connections"""
        logger.debug("New database connection established")
    
    @event.listens_for(engine.sync_engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        """Log connection checkout from pool"""
        logger.debug("Connection checked out from pool")
    
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """
    Create async session factory
    
    Args:
        engine: AsyncEngine instance
        
    Returns:
        Configured async_sessionmaker
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
        autocommit=False,
        autoflush=False,
    )


async def init_db() -> None:
    """
    Initialize database connection pool
    Should be called on application startup
    """
    global _engine, _async_session_factory
    
    logger.info("Initializing database connection pool...")
    
    # Log database connection details for debugging
    db_url = get_database_url()
    logger.info(f"Database URL: {db_url.replace(settings.POSTGRES_PASSWORD, '***')}")
    logger.info(f"Host: {settings.POSTGRES_HOST}, Port: {settings.POSTGRES_PORT}")
    
    # Create engine
    _engine = create_engine()
    
    # Create session factory
    _async_session_factory = create_session_factory(_engine)
    
    # Test connection
    try:
        async with _engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connection pool
    Should be called on application shutdown
    """
    global _engine, _async_session_factory
    
    if _engine:
        logger.info("Closing database connection pool...")
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database connection pool closed")


def get_session_factory() -> async_sessionmaker:
    """
    Get the global session factory
    
    Returns:
        async_sessionmaker instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )
    return _async_session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session with automatic cleanup
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
            await session.commit()
    
    Yields:
        AsyncSession instance
    """
    factory = get_session_factory()
    session = factory()
    
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_session_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session without auto-commit
    Useful for read-only operations
    
    Usage:
        async with get_session_no_commit() as session:
            result = await session.execute(query)
    
    Yields:
        AsyncSession instance
    """
    factory = get_session_factory()
    session = factory()
    
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()


class DatabaseSessionManager:
    """
    Context manager for database sessions with transaction support
    
    Usage:
        async with DatabaseSessionManager() as session:
            # Perform database operations
            result = await session.execute(query)
            # Auto-commit on success, rollback on error
    """
    
    def __init__(self, auto_commit: bool = True):
        """
        Initialize session manager
        
        Args:
            auto_commit: Automatically commit on success
        """
        self.auto_commit = auto_commit
        self.session: Optional[AsyncSession] = None
    
    async def __aenter__(self) -> AsyncSession:
        """Enter context and create session"""
        factory = get_session_factory()
        self.session = factory()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context and cleanup session"""
        if self.session:
            try:
                if exc_type is None and self.auto_commit:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()


async def execute_raw_sql(query: str, params: Optional[dict] = None) -> list:
    """
    Execute raw SQL query
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of result rows
    """
    async with get_session_no_commit() as session:
        result = await session.execute(text(query), params or {})
        return result.fetchall()


async def health_check() -> dict:
    """
    Check database health
    
    Returns:
        Health status dictionary
    """
    try:
        async with get_session_no_commit() as session:
            # Test query
            result = await session.execute(text("SELECT 1 as health"))
            row = result.fetchone()
            
            # Get connection pool stats
            pool = _engine.pool
            
            return {
                "status": "healthy",
                "database": "postgresql",
                "connection_test": row[0] == 1,
                "pool_size": pool.size(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "checked_in": pool.checkedin(),
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# Dependency injection for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with get_session() as session:
        yield session


async def get_db_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for read-only database sessions
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_no_commit)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with get_session_no_commit() as session:
        yield session


# Transaction decorator
def transactional(func):
    """
    Decorator to wrap function in database transaction
    
    Usage:
        @transactional
        async def create_user(name: str):
            async with get_session() as session:
                user = User(name=name)
                session.add(user)
    """
    async def wrapper(*args, **kwargs):
        async with DatabaseSessionManager() as session:
            # Inject session if function accepts it
            if 'session' in func.__code__.co_varnames:
                kwargs['session'] = session
            return await func(*args, **kwargs)
    return wrapper


# Utility functions
async def create_tables() -> None:
    """
    Create all tables defined in Base metadata
    WARNING: Only use in development
    """
    if not settings.DEBUG:
        raise RuntimeError("create_tables() only allowed in DEBUG mode")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_tables() -> None:
    """
    Drop all tables defined in Base metadata
    WARNING: Only use in development
    """
    if not settings.DEBUG:
        raise RuntimeError("drop_tables() only allowed in DEBUG mode")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")


# Export public API
__all__ = [
    "Base",
    "init_db",
    "close_db",
    "get_session",
    "get_session_no_commit",
    "get_db",
    "get_db_no_commit",
    "DatabaseSessionManager",
    "execute_raw_sql",
    "health_check",
    "transactional",
    "create_tables",
    "drop_tables",
]

# Made with Codex
