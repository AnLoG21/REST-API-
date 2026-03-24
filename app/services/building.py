from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.building import BuildingRepository
from app.models import Building
from app.schemas import BuildingCreate
from app.core.exceptions import NotFoundException


class BuildingService:
    def __init__(self, db: AsyncSession):
        self.building_repo = BuildingRepository(db)

    async def get_building(self, building_id: int) -> Building:
        building = await self.building_repo.get(building_id)
        if not building:
            raise NotFoundException('Building', building_id)
        return building

    async def get_all_buildings(self) -> List[Building]:
        return await self.building_repo.get_all()

    async def create_building(self, building_data: BuildingCreate) -> Building:
        db_building = Building(**building_data.model_dump())
        return await self.building_repo.create(db_building)

