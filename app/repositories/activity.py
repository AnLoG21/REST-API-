from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Activity
from app.repositories.base import BaseRepository
from app.core.logger import logger


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: AsyncSession):
        super().__init__(Activity, db)

    async def get_tree_ids(self, activity_id: int) -> List[int]:
        activity_ids = [activity_id]

        async def get_children(parent_id: int):
            try:
                result = await self.db.execute(select(Activity).where(Activity.parent_id == parent_id))
                children = result.scalars().all()
                for child in children:
                    activity_ids.append(child.id)
                    await get_children(child.id)
            except Exception as e:
                logger.error(f'Error getting activity tree: {e}')
                raise

        await get_children(activity_id)
        return activity_ids

    async def get_level(self, activity_id: int) -> int:
        try:
            activity = await self.get(activity_id)
            if not activity:
                return 0

            if activity.parent_id is None:
                return 1

            return 1 + await self.get_level(activity.parent_id)
        except Exception as e:
            logger.error(f'Error getting activity level: {e}')
            raise

    async def validate_nesting_level(self, parent_id: int) -> bool:
        try:
            parent_level = await self.get_level(parent_id)
            return parent_level < 3
        except Exception as e:
            logger.error(f'Error validating nesting level: {e}')
            raise

