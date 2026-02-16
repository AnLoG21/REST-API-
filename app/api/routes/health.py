from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.logger import logger

router = APIRouter(prefix='/health', tags=['health'])


@router.get('')
def health_check():
    return {'status': 'healthy'}


@router.get('/ready')
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {'status': 'ready', 'database': 'connected'}
    except Exception as e:
        logger.error(f'Database connection check failed: {e}')
        return {'status': 'not ready', 'database': 'disconnected'}

