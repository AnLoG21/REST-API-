from typing import List
from sqlalchemy.orm import Session
from app.models import Activity
from app.repositories.base import BaseRepository
from app.core.logger import logger


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: Session):
        super().__init__(Activity, db)

    def get_tree_ids(self, activity_id: int) -> List[int]:
        activity_ids = [activity_id]
        
        def get_children(parent_id: int):
            try:
                children = self.db.query(Activity).filter(Activity.parent_id == parent_id).all()
                for child in children:
                    activity_ids.append(child.id)
                    get_children(child.id)
            except Exception as e:
                logger.error(f'Error getting activity tree: {e}')
                raise
        
        get_children(activity_id)
        return activity_ids

    def get_level(self, activity_id: int) -> int:
        try:
            activity = self.get(activity_id)
            if not activity:
                return 0
            
            if activity.parent_id is None:
                return 1
            
            return 1 + self.get_level(activity.parent_id)
        except Exception as e:
            logger.error(f'Error getting activity level: {e}')
            raise

    def validate_nesting_level(self, parent_id: int) -> bool:
        try:
            parent_level = self.get_level(parent_id)
            return parent_level < 3
        except Exception as e:
            logger.error(f'Error validating nesting level: {e}')
            raise

