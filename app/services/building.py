from typing import List
from sqlalchemy.orm import Session
from app.repositories.building import BuildingRepository
from app.models import Building
from app.schemas import BuildingCreate
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class BuildingService:
    def __init__(self, db: Session):
        self.building_repo = BuildingRepository(db)

    def get_building(self, building_id: int) -> Building:
        building = self.building_repo.get(building_id)
        if not building:
            raise NotFoundException('Building', building_id)
        return building

    def get_all_buildings(self) -> List[Building]:
        return self.building_repo.get_all()

    def create_building(self, building_data: BuildingCreate) -> Building:
        db_building = Building(**building_data.dict())
        return self.building_repo.create(db_building)

