from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.logger import logger

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key or api_key != settings.API_KEY:
        logger.warning(f'Invalid API key attempt: {api_key}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid API Key'
        )
    return api_key


def get_database(db: Session = Depends(get_db)) -> Session:
    return db

