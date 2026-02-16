from typing import List
from sqlalchemy.orm import Session
from app.repositories.activity import ActivityRepository
from app.models import Activity
from app.schemas import ActivityCreate
from app.core.exceptions import NotFoundException, ActivityNestingLevelException
from app.core.logger import logger


class ActivityService:
    def __init__(self, db: Session):
        self.activity_repo = ActivityRepository(db)

    def get_activity(self, activity_id: int) -> Activity:
        activity = self.activity_repo.get(activity_id)
        if not activity:
            raise NotFoundException('Activity', activity_id)
        return activity

    def get_all_activities(self) -> List[Activity]:
        return self.activity_repo.get_all()

    def create_activity(self, activity_data: ActivityCreate) -> Activity:
        if activity_data.parent_id:
            if not self.activity_repo.validate_nesting_level(activity_data.parent_id):
                raise ActivityNestingLevelException()
        
        db_activity = Activity(**activity_data.dict())
        return self.activity_repo.create(db_activity)

    def get_tree_ids(self, activity_id: int) -> List[int]:
        activity = self.get_activity(activity_id)
        return self.activity_repo.get_tree_ids(activity_id)

