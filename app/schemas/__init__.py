from pydantic import BaseModel, computed_field
from typing import List, Optional


class PhoneBase(BaseModel):
    number: str


class PhoneCreate(PhoneBase):
    pass


class Phone(PhoneBase):
    id: int

    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int


class OrganizationCreate(BaseModel):
    name: str
    building_id: int
    phone_numbers: List[str] = []
    activity_ids: List[int] = []


class Organization(OrganizationBase):
    id: int
    building: Building
    phones: List[Phone] = []
    activities: List[Activity] = []

    class Config:
        from_attributes = True
    
    @computed_field
    @property
    def phone_numbers(self) -> List[str]:
        return [phone.number for phone in self.phones]
    
    @computed_field
    @property
    def activity_ids(self) -> List[int]:
        return [activity.id for activity in self.activities]


Activity.model_rebuild()

