from app.database import Base
from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from geoalchemy2 import Geometry
from geoalchemy2.shape import WKBElement
from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    WASHER = "washer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.OWNER)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_email_verified: Mapped[bool] = mapped_column(default=False)
    phone_number: Mapped[str] = mapped_column(unique=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    profile_image: Mapped[str] = mapped_column(nullable=True)
    user_role: Mapped[str] = mapped_column(nullable=False)
    is_flagged: Mapped[bool] = mapped_column(default=False)
    is_restricted: Mapped[bool] = mapped_column(default=False)
    is_deactivated: Mapped[bool] = mapped_column(default=False)

    payment_method: Mapped[str] = mapped_column(nullable=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(nullable=True, default=None, onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
    address = relationship("Address", back_populates="profile", cascade="all, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "profile",
        "polymorphic_on": user_role
    }

class Address(Base):
    __tablename__ = "address"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    address1: Mapped[str]
    address2: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str]
    state: Mapped[str]
    country: Mapped[str]
    geom: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POINT", srid=4326))

    profile = relationship("Profile", back_populates="address")

class Notifications(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    title: Mapped[str]
    message: Mapped[str]
    is_read: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    created: Mapped[str] = mapped_column(default=datetime.now(timezone.utc))

    messages = relationship("IssueMessage", back_populates="issue", cascade="all, delete-orphan")


class IssueMessage(Base):
    __tablename__ = "issue_messages"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    issue_id: Mapped[str] = mapped_column(ForeignKey("issues.id"), nullable=False)
    profile_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    body: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    issue = relationship("Issue", back_populates="messages")
