from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Building
from app.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    def __init__(self, db: AsyncSession):
        super().__init__(Building, db)

