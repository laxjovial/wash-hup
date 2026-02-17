from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from geoalchemy2 import Geometry
from geoalchemy2.shape import WKBElement
from datetime import datetime, timezone
from enum import StrEnum


class WashType(StrEnum):
    QUICK = 'quick'
    SMART = 'smart'
    PREMIUM = 'premium' 

class Wash(Base):
    __tablename__ = 'washes'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[str] = mapped_column(ForeignKey('owner_profile.id'), nullable=False)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'), default=None)
    location_id: Mapped[str] = mapped_column(ForeignKey('location.id'))

    client_name: Mapped[str] = mapped_column(default=None)
    client_pic: Mapped[str] = mapped_column(default=None)
    washer_name: Mapped[str] = mapped_column(default=None)
    washer_pic: Mapped[str] = mapped_column(default=None)
    washer_rating: Mapped[float] = mapped_column(default=None)
    car_name: Mapped[str] = mapped_column(default=None)
    location: Mapped[str] = mapped_column(default=None)

    bucket_avl: Mapped[bool]
    water_avl: Mapped[bool]
    wash_type: Mapped[WashType]
    price: Mapped[float] = mapped_column(default=0.0)

    accepted: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    started: Mapped[bool] = mapped_column(default=False)
    time_started: Mapped[datetime] = mapped_column(default=None)

    image: Mapped[str] = mapped_column(default=None)
    completed: Mapped[bool] = mapped_column(default=False)
    time_completed: Mapped[datetime] = mapped_column(default=None)

    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    
    # --- relationships
    cars = relationship('Car', back_populates='wash', cascade='all, delete-orphan')
    location = relationship('Location', back_populates='wash')
    rating = relationship('Review', back_populates='wash')
    

class Location(Base):
    __tablename__ = 'location'
    
    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    location: Mapped[str]
    geom: Mapped[WKBElement] = mapped_column(Geometry(geometry_type='POINT', srid=4326))

    wash = relationship('Wash', back_populates='location', cascade="all, delete-orphan")

class Car(Base):
    __tablename__ = "cars"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    wash_id: Mapped[str] = mapped_column(ForeignKey('washes.id'), nullable=False)
    car_type: Mapped[str]
    car_name: Mapped[str]
    color: Mapped[str]

    wash = relationship('Wash', back_populates='cars')

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    wash_id: Mapped[str] = mapped_column(ForeignKey('washes.id'), nullable=False)
    client_id: Mapped[str] = mapped_column(ForeignKey("owner_profile.id"), nullable=False)
    washer_id: Mapped[str] = mapped_column(ForeignKey("washer_profile.id"), nullable=False)
    rating: Mapped[float]
    review: Mapped[str] = mapped_column(default=None)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    wash = relationship("Wash", back_populates="rating")

class WashMessage(Base):
    __tablename__ = 'wash_messages'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    wash_id: Mapped[str] = mapped_column(ForeignKey('washes.id'), nullable=False)
    sender_id: Mapped[str] = mapped_column(ForeignKey('profile.id'), nullable=False)
    body: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))