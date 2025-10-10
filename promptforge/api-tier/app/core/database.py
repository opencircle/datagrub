"""
Database connection and session management
Uses SQLAlchemy 2.0 async engine with asyncpg driver

Performance Optimizations:
- asyncpg driver for high-performance PostgreSQL access
- Connection pooling (configurable pool size and overflow)
- Pool health checks (pre-ping)
- Connection recycling (prevent stale connections)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,

    # Connection Pool Configuration (Performance)
    pool_size=settings.DB_POOL_SIZE,              # Base connections (20)
    max_overflow=settings.DB_MAX_OVERFLOW,        # Additional when needed (30)
    pool_recycle=settings.DB_POOL_RECYCLE,        # Recycle after 1 hour
    pool_pre_ping=settings.DB_POOL_PRE_PING,      # Health check
    pool_timeout=settings.DB_POOL_TIMEOUT,        # Connection timeout
    echo_pool=settings.DB_ECHO_POOL,              # Log pool events

    # Performance optimizations
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for predictable performance
        },
        "command_timeout": 60,  # Query timeout
        "timeout": 10,  # Connection timeout
    },
)

logger.info(
    f"Database engine initialized: pool_size={settings.DB_POOL_SIZE}, "
    f"max_overflow={settings.DB_MAX_OVERFLOW}, driver=asyncpg"
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database sessions.
    Use in FastAPI route dependencies.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
