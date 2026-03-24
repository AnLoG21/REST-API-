from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.schemas import Organization as OrganizationSchema, OrganizationCreate
from app.services.organization import OrganizationService
from app.api.dependencies import verify_api_key, get_database

router = APIRouter(prefix='/organizations', tags=['organizations'])


@router.get('/{organization_id}', response_model=OrganizationSchema, dependencies=[Depends(verify_api_key)])
async def get_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_database)
):
    service = OrganizationService(db)
    return await service.get_organization(organization_id)


@router.get('', response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
async def list_organizations(
    building_id: Optional[int] = Query(None, description='ID здания'),
    activity_id: Optional[int] = Query(None, description='ID вида деятельности'),
    name: Optional[str] = Query(None, description='Поиск по названию организации'),
    latitude: Optional[float] = Query(None, description='Широта центра поиска'),
    longitude: Optional[float] = Query(None, description='Долгота центра поиска'),
    radius: Optional[float] = Query(None, description='Радиус поиска в километрах'),
    min_lat: Optional[float] = Query(None, description='Минимальная широта для прямоугольной области'),
    max_lat: Optional[float] = Query(None, description='Максимальная широта для прямоугольной области'),
    min_lon: Optional[float] = Query(None, description='Минимальная долгота для прямоугольной области'),
    max_lon: Optional[float] = Query(None, description='Максимальная долгота для прямоугольной области'),
    db: AsyncSession = Depends(get_database)
):
    service = OrganizationService(db)
    return await service.get_organizations(
        building_id=building_id,
        activity_id=activity_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon
    )


@router.post('', response_model=OrganizationSchema, dependencies=[Depends(verify_api_key)])
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_database)
):
    service = OrganizationService(db)
    return await service.create_organization(organization)

