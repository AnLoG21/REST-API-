from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas import Activity as ActivitySchema, ActivityCreate
from app.services.activity import ActivityService
from app.services.organization import OrganizationService
from app.api.dependencies import verify_api_key, get_database
from app.schemas import Organization as OrganizationSchema

router = APIRouter(prefix='/activities', tags=['activities'])


@router.get('/{activity_id}/organizations', response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
def list_organizations_by_activity(
    activity_id: int,
    db: Session = Depends(get_database)
):
    service = OrganizationService(db)
    return service.get_by_activity(activity_id)


@router.post('', response_model=ActivitySchema, dependencies=[Depends(verify_api_key)])
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_database)
):
    service = ActivityService(db)
    return service.create_activity(activity)

