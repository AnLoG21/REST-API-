from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from app.core.logger import logger

ASYNC_DATABASE_URL = (
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    if settings.DATABASE_URL.startswith("postgresql://")
    else settings.DATABASE_URL
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
        logger.debug('Database session created')
    except Exception as e:
        logger.error(f'Database session error: {e}')
        await db.rollback()
        raise
    finally:
        await db.close()
        logger.debug('Database session closed')

