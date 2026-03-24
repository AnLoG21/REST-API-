from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True)
)

organization_phone = Table(
    'organization_phone',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('phone_id', Integer, ForeignKey('phones.id'), primary_key=True)
)


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization", back_populates="building")


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False, unique=True)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)

    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship("Organization", secondary=organization_activity, back_populates="activities")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)

    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activity, back_populates="organizations")
    phones = relationship("Phone", secondary=organization_phone)

