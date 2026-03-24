from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas import Activity as ActivitySchema, ActivityCreate
from app.services.activity import ActivityService
from app.services.organization import OrganizationService
from app.api.dependencies import verify_api_key, get_database
from app.schemas import Organization as OrganizationSchema

router = APIRouter(prefix='/activities', tags=['activities'])


@router.get('/{activity_id}/organizations', response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
async def list_organizations_by_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_database)
):
    service = OrganizationService(db)
    return await service.get_by_activity(activity_id)


@router.post('', response_model=ActivitySchema, dependencies=[Depends(verify_api_key)])
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_database)
):
    service = ActivityService(db)
    return await service.create_activity(activity)

