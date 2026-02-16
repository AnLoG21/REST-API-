from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.organization import OrganizationRepository
from app.repositories.building import BuildingRepository
from app.repositories.activity import ActivityRepository
from app.models import Organization, Phone
from app.schemas import OrganizationCreate
from app.core.exceptions import NotFoundException, ValidationException
from app.core.logger import logger


class OrganizationService:
    def __init__(self, db: Session):
        self.organization_repo = OrganizationRepository(db)
        self.building_repo = BuildingRepository(db)
        self.activity_repo = ActivityRepository(db)

    def get_organization(self, organization_id: int) -> Organization:
        organization = self.organization_repo.get_with_relations(organization_id)
        if not organization:
            raise NotFoundException('Organization', organization_id)
        return organization

    def get_organizations(
        self,
        building_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        name: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[float] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
    ) -> List[Organization]:
        organizations = self.organization_repo.get_all_with_relations()
        
        if building_id:
            organizations = [org for org in organizations if org.building_id == building_id]
        
        if activity_id:
            activity_ids = self.activity_repo.get_tree_ids(activity_id)
            organizations = self.organization_repo.get_by_activity_ids(activity_ids)
            if building_id or name or latitude or min_lat:
                organizations = self._apply_filters(organizations, building_id, name, latitude, longitude, radius, min_lat, max_lat, min_lon, max_lon)
        
        if name:
            if activity_id:
                organizations = [org for org in organizations if name.lower() in org.name.lower()]
            else:
                organizations = self.organization_repo.search_by_name(name)
                if building_id:
                    organizations = [org for org in organizations if org.building_id == building_id]
        
        if latitude is not None and longitude is not None and radius is not None:
            if activity_id or name or building_id:
                organizations = [org for org in organizations 
                               if self._is_in_radius(org.building.latitude, org.building.longitude, latitude, longitude, radius)]
            else:
                organizations = self.organization_repo.get_in_radius(latitude, longitude, radius)
        
        if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
            if activity_id or name or building_id or (latitude and longitude and radius):
                organizations = [org for org in organizations 
                               if (min_lat <= org.building.latitude <= max_lat and 
                                   min_lon <= org.building.longitude <= max_lon)]
            else:
                organizations = self.organization_repo.get_in_rectangle(min_lat, max_lat, min_lon, max_lon)
        
        return list(set(organizations))

    def _apply_filters(
        self,
        organizations: List[Organization],
        building_id: Optional[int],
        name: Optional[str],
        latitude: Optional[float],
        longitude: Optional[float],
        radius: Optional[float],
        min_lat: Optional[float],
        max_lat: Optional[float],
        min_lon: Optional[float],
        max_lon: Optional[float],
    ) -> List[Organization]:
        if building_id:
            organizations = [org for org in organizations if org.building_id == building_id]
        if name:
            organizations = [org for org in organizations if name.lower() in org.name.lower()]
        if latitude and longitude and radius:
            organizations = [org for org in organizations 
                           if self._is_in_radius(org.building.latitude, org.building.longitude, latitude, longitude, radius)]
        if min_lat and max_lat and min_lon and max_lon:
            organizations = [org for org in organizations 
                           if (min_lat <= org.building.latitude <= max_lat and 
                               min_lon <= org.building.longitude <= max_lon)]
        return organizations

    def _is_in_radius(self, lat1: float, lon1: float, lat2: float, lon2: float, radius: float) -> bool:
        import math
        lat_delta = radius / 111.0
        lon_delta = radius / (111.0 * math.cos(math.radians(lat2)))
        return (lat2 - lat_delta <= lat1 <= lat2 + lat_delta and 
                lon2 - lon_delta <= lon1 <= lon2 + lon_delta)

    def get_by_building(self, building_id: int) -> List[Organization]:
        building = self.building_repo.get(building_id)
        if not building:
            raise NotFoundException('Building', building_id)
        return self.organization_repo.get_by_building(building_id)

    def get_by_activity(self, activity_id: int) -> List[Organization]:
        activity = self.activity_repo.get(activity_id)
        if not activity:
            raise NotFoundException('Activity', activity_id)
        activity_ids = self.activity_repo.get_tree_ids(activity_id)
        return self.organization_repo.get_by_activity_ids(activity_ids)

    def create_organization(self, organization_data: OrganizationCreate) -> Organization:
        building = self.building_repo.get(organization_data.building_id)
        if not building:
            raise NotFoundException('Building', organization_data.building_id)
        
        for activity_id in organization_data.activity_ids:
            if not self.activity_repo.validate_nesting_level(activity_id):
                raise ValidationException(f'Activity {activity_id} exceeds maximum nesting level of 3')
        
        from app.models import Organization as OrgModel
        db_organization = OrgModel(
            name=organization_data.name,
            building_id=organization_data.building_id
        )
        
        db = self.organization_repo.db
        
        for phone_number in organization_data.phone_numbers:
            phone = db.query(Phone).filter(Phone.number == phone_number).first()
            if not phone:
                phone = Phone(number=phone_number)
                db.add(phone)
                db.flush()
            db_organization.phones.append(phone)
        
        from app.models import Activity
        activities = db.query(Activity).filter(Activity.id.in_(organization_data.activity_ids)).all()
        db_organization.activities = activities
        
        return self.organization_repo.create(db_organization)

