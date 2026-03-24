from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base
from app.core.logger import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        try:
            result = await self.db.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f'Error getting {self.model.__name__} with id {id}: {e}')
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            result = await self.db.execute(select(self.model).offset(skip).limit(limit))
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f'Error getting all {self.model.__name__}: {e}')
            raise

    async def create(self, obj: ModelType) -> ModelType:
        try:
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f'Created {self.model.__name__} with id {obj.id}')
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f'Error creating {self.model.__name__}: {e}')
            raise

    async def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        try:
            obj = await self.get(id)
            if not obj:
                return None
            for key, value in obj_data.items():
                setattr(obj, key, value)
            await self.db.commit()
            await self.db.refresh(obj)
            logger.info(f'Updated {self.model.__name__} with id {id}')
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f'Error updating {self.model.__name__} with id {id}: {e}')
            raise

    async def delete(self, id: int) -> bool:
        try:
            obj = await self.get(id)
            if not obj:
                return False
            await self.db.delete(obj)
            await self.db.commit()
            logger.info(f'Deleted {self.model.__name__} with id {id}')
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f'Error deleting {self.model.__name__} with id {id}: {e}')
            raise

