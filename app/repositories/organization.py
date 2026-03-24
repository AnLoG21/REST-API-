from typing import List, Optional
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models import Organization, Building, Activity
from app.repositories.base import BaseRepository
from app.core.logger import logger


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)

    async def get_with_relations(self, id: int) -> Optional[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .where(Organization.id == id)
            )
            result = await self.db.execute(stmt)
            return result.unique().scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting organization with relations: {e}')
            raise

    async def get_by_building(self, building_id: int) -> List[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .where(Organization.building_id == building_id)
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error getting organizations by building: {e}')
            raise

    async def get_by_activity_ids(self, activity_ids: List[int]) -> List[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .join(Organization.activities)
                .where(Activity.id.in_(activity_ids))
                .distinct()
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error getting organizations by activities: {e}')
            raise

    async def search_by_name(self, name: str) -> List[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .where(Organization.name.ilike(f'%{name}%'))
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error searching organizations by name: {e}')
            raise

    async def get_in_radius(self, latitude: float, longitude: float, radius: float) -> List[Organization]:
        try:
            import math
            lat_delta = radius / 111.0
            lon_delta = radius / (111.0 * math.cos(math.radians(latitude)))

            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .join(Building)
                .where(
                    and_(
                        Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
                        Building.longitude.between(longitude - lon_delta, longitude + lon_delta),
                    )
                )
                .distinct()
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error getting organizations in radius: {e}')
            raise

    async def get_in_rectangle(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .join(Building)
                .where(
                    and_(
                        Building.latitude.between(min_lat, max_lat),
                        Building.longitude.between(min_lon, max_lon),
                    )
                )
                .distinct()
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error getting organizations in rectangle: {e}')
            raise

    async def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        try:
            stmt = (
                select(Organization)
                .options(
                    joinedload(Organization.building),
                    joinedload(Organization.phones),
                    joinedload(Organization.activities),
                )
                .offset(skip)
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return list(result.unique().scalars().all())
        except Exception as e:
            logger.error(f'Error getting all organizations with relations: {e}')
            raise

