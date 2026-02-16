from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models import Organization, Building, Activity
from app.repositories.base import BaseRepository
from app.core.logger import logger


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: Session):
        super().__init__(Organization, db)

    def get_with_relations(self, id: int) -> Optional[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).filter(Organization.id == id).first()
        except Exception as e:
            logger.error(f'Error getting organization with relations: {e}')
            raise

    def get_by_building(self, building_id: int) -> List[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).filter(Organization.building_id == building_id).all()
        except Exception as e:
            logger.error(f'Error getting organizations by building: {e}')
            raise

    def get_by_activity_ids(self, activity_ids: List[int]) -> List[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).join(Organization.activities).filter(
                Activity.id.in_(activity_ids)
            ).distinct().all()
        except Exception as e:
            logger.error(f'Error getting organizations by activities: {e}')
            raise

    def search_by_name(self, name: str) -> List[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).filter(Organization.name.ilike(f'%{name}%')).all()
        except Exception as e:
            logger.error(f'Error searching organizations by name: {e}')
            raise

    def get_in_radius(self, latitude: float, longitude: float, radius: float) -> List[Organization]:
        try:
            import math
            lat_delta = radius / 111.0
            lon_delta = radius / (111.0 * math.cos(math.radians(latitude)))
            
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).join(Building).filter(
                and_(
                    Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
                    Building.longitude.between(longitude - lon_delta, longitude + lon_delta)
                )
            ).distinct().all()
        except Exception as e:
            logger.error(f'Error getting organizations in radius: {e}')
            raise

    def get_in_rectangle(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).join(Building).filter(
                and_(
                    Building.latitude.between(min_lat, max_lat),
                    Building.longitude.between(min_lon, max_lon)
                )
            ).distinct().all()
        except Exception as e:
            logger.error(f'Error getting organizations in rectangle: {e}')
            raise

    def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        try:
            return self.db.query(Organization).options(
                joinedload(Organization.building),
                joinedload(Organization.phones),
                joinedload(Organization.activities)
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f'Error getting all organizations with relations: {e}')
            raise

