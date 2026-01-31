from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
import math

from database import get_db
from models import Organization, Building, Activity, Phone
from schemas import (
    Organization as OrganizationSchema,
    Building as BuildingSchema,
    Activity as ActivitySchema,
    OrganizationCreate,
    BuildingCreate,
    ActivityCreate
)
from auth import verify_api_key

app = FastAPI(
    title="Organizations Directory API",
    description="REST API для справочника Организаций, Зданий и Деятельностей",
    version="1.0.0"
)


def get_activity_tree_ids(activity_id: int, db: Session) -> List[int]:
    activity_ids = [activity_id]
    
    def get_children(parent_id: int):
        children = db.query(Activity).filter(Activity.parent_id == parent_id).all()
        for child in children:
            activity_ids.append(child.id)
            get_children(child.id)
    
    get_children(activity_id)
    return activity_ids


def get_activity_level(activity_id: int, db: Session) -> int:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return 0
    
    if activity.parent_id is None:
        return 1
    
    return 1 + get_activity_level(activity.parent_id, db)


def validate_activity_levels(parent_id: int, db: Session) -> bool:
    parent_level = get_activity_level(parent_id, db)
    if parent_level >= 3:
        return False
    return True


@app.get("/")
async def root():
    return {"message": "Organizations Directory API"}


@app.get("/organizations/{organization_id}", response_model=OrganizationSchema, dependencies=[Depends(verify_api_key)])
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    organization = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.phones),
        joinedload(Organization.activities)
    ).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


@app.get("/organizations", response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
def list_organizations(
    building_id: Optional[int] = Query(None, description="ID здания"),
    activity_id: Optional[int] = Query(None, description="ID вида деятельности"),
    name: Optional[str] = Query(None, description="Поиск по названию организации"),
    latitude: Optional[float] = Query(None, description="Широта центра поиска"),
    longitude: Optional[float] = Query(None, description="Долгота центра поиска"),
    radius: Optional[float] = Query(None, description="Радиус поиска в километрах"),
    min_lat: Optional[float] = Query(None, description="Минимальная широта для прямоугольной области"),
    max_lat: Optional[float] = Query(None, description="Максимальная широта для прямоугольной области"),
    min_lon: Optional[float] = Query(None, description="Минимальная долгота для прямоугольной области"),
    max_lon: Optional[float] = Query(None, description="Максимальная долгота для прямоугольной области"),
    db: Session = Depends(get_db)
):
    query = db.query(Organization)
    
    if building_id:
        query = query.filter(Organization.building_id == building_id)
    
    if activity_id:
        activity_ids = get_activity_tree_ids(activity_id, db)
        query = query.join(Organization.activities).filter(Activity.id.in_(activity_ids))
    
    if name:
        query = query.filter(Organization.name.ilike(f"%{name}%"))
    
    if latitude is not None and longitude is not None and radius is not None:
        lat_delta = radius / 111.0
        lon_delta = radius / (111.0 * math.cos(math.radians(latitude)))
        
        query = query.join(Building).filter(
            Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
            Building.longitude.between(longitude - lon_delta, longitude + lon_delta)
        )
    
    if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
        query = query.join(Building).filter(
            Building.latitude.between(min_lat, max_lat),
            Building.longitude.between(min_lon, max_lon)
        )
    
    organizations = query.options(
        joinedload(Organization.building),
        joinedload(Organization.phones),
        joinedload(Organization.activities)
    ).distinct().all()
    return organizations


@app.get("/buildings", response_model=List[BuildingSchema], dependencies=[Depends(verify_api_key)])
def list_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).all()
    return buildings


@app.get("/buildings/{building_id}/organizations", response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
def list_organizations_by_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.phones),
        joinedload(Organization.activities)
    ).filter(Organization.building_id == building_id).all()
    return organizations


@app.get("/activities/{activity_id}/organizations", response_model=List[OrganizationSchema], dependencies=[Depends(verify_api_key)])
def list_organizations_by_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity_ids = get_activity_tree_ids(activity_id, db)
    organizations = db.query(Organization).options(
        joinedload(Organization.building),
        joinedload(Organization.phones),
        joinedload(Organization.activities)
    ).join(Organization.activities).filter(
        Activity.id.in_(activity_ids)
    ).distinct().all()
    
    return organizations


@app.post("/buildings", response_model=BuildingSchema, dependencies=[Depends(verify_api_key)])
def create_building(building: BuildingCreate, db: Session = Depends(get_db)):
    db_building = Building(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building


@app.post("/activities", response_model=ActivitySchema, dependencies=[Depends(verify_api_key)])
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    if activity.parent_id:
        if not validate_activity_levels(activity.parent_id, db):
            raise HTTPException(status_code=400, detail="Maximum activity nesting level is 3")
    
    db_activity = Activity(**activity.dict())
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


@app.post("/organizations", response_model=OrganizationSchema, dependencies=[Depends(verify_api_key)])
def create_organization(organization: OrganizationCreate, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == organization.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    
    for activity_id in organization.activity_ids:
        if not validate_activity_levels(activity_id, db):
            raise HTTPException(status_code=400, detail=f"Activity {activity_id} exceeds maximum nesting level of 3")
    
    db_organization = Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    db.add(db_organization)
    db.flush()
    
    for phone_number in organization.phone_numbers:
        phone = db.query(Phone).filter(Phone.number == phone_number).first()
        if not phone:
            phone = Phone(number=phone_number)
            db.add(phone)
            db.flush()
        db_organization.phones.append(phone)
    
    activities = db.query(Activity).filter(Activity.id.in_(organization.activity_ids)).all()
    db_organization.activities = activities
    
    db.commit()
    db.refresh(db_organization)
    return db_organization

