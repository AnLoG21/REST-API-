from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import BaseAPIException
from app.api.routes import organizations, buildings, activities, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Starting application...')
    yield
    logger.info('Shutting down application...')


app = FastAPI(
    title=settings.PROJECT_NAME,
    description='REST API для справочника Организаций, Зданий и Деятельностей',
    version=settings.VERSION,
    lifespan=lifespan
)


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    logger.warning(f'API exception: {exc.detail}')
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f'Validation error: {exc.errors()}')
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': exc.errors()}
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f'Database error: {str(exc)}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Database error occurred'}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unexpected error: {str(exc)}', exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'Internal server error'}
    )


@app.get('/')
async def root():
    return {'message': f'{settings.PROJECT_NAME} v{settings.VERSION}'}


app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)
app.include_router(health.router)

