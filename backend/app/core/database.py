"""
A.B.E.L - Database Configuration
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def get_database_url() -> str:
    """Get database URL with fallback to SQLite for development."""
    url = settings.database_url

    # Default to SQLite if no URL configured or if it contains unresolved variables
    if not url or "${" in url or url.endswith(":"):
        return "sqlite+aiosqlite:///./abel.db"

    # Convert postgresql to asyncpg if needed
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")

    return url


# Get the database URL
db_url = get_database_url()

# Create async engine with appropriate settings
if db_url.startswith("sqlite"):
    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(
        db_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
