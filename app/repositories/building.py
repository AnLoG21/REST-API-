from sqlalchemy.orm import Session
from app.models import Building
from app.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[Building]):
    def __init__(self, db: Session):
        super().__init__(Building, db)

