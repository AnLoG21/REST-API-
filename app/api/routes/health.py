from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.logger import logger

router = APIRouter(prefix='/health', tags=['health'])


@router.get('')
def health_check():
    return {'status': 'healthy'}


@router.get('/ready')
async def readiness_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text('SELECT 1'))
        return {'status': 'ready', 'database': 'connected'}
    except Exception as e:
        logger.error(f'Database connection check failed: {e}')
        return {'status': 'not ready', 'database': 'disconnected'}

