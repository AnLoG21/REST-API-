from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.activity import ActivityRepository
from app.models import Activity
from app.schemas import ActivityCreate
from app.core.exceptions import NotFoundException, ActivityNestingLevelException


class ActivityService:
    def __init__(self, db: AsyncSession):
        self.activity_repo = ActivityRepository(db)

    async def get_activity(self, activity_id: int) -> Activity:
        activity = await self.activity_repo.get(activity_id)
        if not activity:
            raise NotFoundException('Activity', activity_id)
        return activity

    async def get_all_activities(self) -> List[Activity]:
        return await self.activity_repo.get_all()

    async def create_activity(self, activity_data: ActivityCreate) -> Activity:
        if activity_data.parent_id:
            if not await self.activity_repo.validate_nesting_level(activity_data.parent_id):
                raise ActivityNestingLevelException()

        db_activity = Activity(**activity_data.model_dump())
        return await self.activity_repo.create(db_activity)

    async def get_tree_ids(self, activity_id: int) -> List[int]:
        await self.get_activity(activity_id)
        return await self.activity_repo.get_tree_ids(activity_id)

