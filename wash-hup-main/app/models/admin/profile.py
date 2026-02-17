from sqlalchemy import ForeignKey, Enum as SQLEnum
from enum import Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from app.database import Base
from app.models.auth.user import Profile



class AdminProfile(Profile):
    __tablename__ = 'admin_profile'

    id: Mapped[str] = mapped_column(ForeignKey('profile.id'), primary_key=True)

    discounts = relationship("Discounts", back_populates="creator")
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

class Category(str, Enum):
    OWNER = 'owner'
    WASHER = 'washer'

class Faqs(Base):
    __tablename__ = 'faqs'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False)
    question: Mapped[str]
    answer: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(default=None, onupdate=datetime.now(timezone.utc))

class TermsAndConditions(Base):
    __tablename__ = 'terms_and_conditions'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False)
    terms: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

class VerificationRequest(Base):
    __tablename__ = 'verification_request'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'), nullable=False)
    category: Mapped[str]
    seen: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
