from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base
from app.core.logger import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f'Error getting {self.model.__name__} with id {id}: {e}')
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f'Error getting all {self.model.__name__}: {e}')
            raise

    def create(self, obj: ModelType) -> ModelType:
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f'Created {self.model.__name__} with id {obj.id}')
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f'Error creating {self.model.__name__}: {e}')
            raise

    def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        try:
            obj = self.get(id)
            if not obj:
                return None
            for key, value in obj_data.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
            logger.info(f'Updated {self.model.__name__} with id {id}')
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f'Error updating {self.model.__name__} with id {id}: {e}')
            raise

    def delete(self, id: int) -> bool:
        try:
            obj = self.get(id)
            if not obj:
                return False
            self.db.delete(obj)
            self.db.commit()
            logger.info(f'Deleted {self.model.__name__} with id {id}')
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f'Error deleting {self.model.__name__} with id {id}: {e}')
            raise

