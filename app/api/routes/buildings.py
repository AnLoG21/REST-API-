from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas import Building as BuildingSchema, BuildingCreate
from app.services.building import BuildingService
from app.services.organization import OrganizationService
from app.api.dependencies import verify_api_key, get_database
from app.schemas import Organization as OrganizationSchema

router = APIRouter(prefix='/buildings', tags=['buildings'])


@router.get('', response_model=List[BuildingSchema], dependencies=[Depends(verify_api_key)])
async def list_buildings(db: AsyncSession = Depends(get_database)):
    service = BuildingService(db)
    return await service.get_all_buildings()


@router.get('/{building_id}/organizations', response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
async def list_organizations_by_building(
    building_id: int,
    db: AsyncSession = Depends(get_database)
):
    service = OrganizationService(db)
    return await service.get_by_building(building_id)


@router.post('', response_model=BuildingSchema, dependencies=[Depends(verify_api_key)])
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_database)
):
    service = BuildingService(db)
    return await service.create_building(building)

