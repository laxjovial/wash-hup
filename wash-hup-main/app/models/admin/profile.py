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
    verification_handled = relationship("VerificationRequest", back_populates="handler")
    faqs = relationship("Faqs", back_populates="admin")
    terms = relationship("TermsAndConditions", back_populates="admin")
    
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

class Category(str, Enum):
    OWNER = 'owner'
    WASHER = 'washer'

class VerificationStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class Faqs(Base):
    __tablename__ = 'faqs'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False)
    question: Mapped[str]
    answer: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(nullable=True, default=None, onupdate=datetime.now(timezone.utc))

    admin = relationship("AdminProfile", back_populates="faqs")

class TermsAndConditions(Base):
    __tablename__ = 'terms_and_conditions'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)
    category: Mapped[Category] = mapped_column(SQLEnum(Category), nullable=False)
    terms: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    admin = relationship("AdminProfile", back_populates="terms")

class VerificationRequest(Base):
    __tablename__ = 'verification_request'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'), nullable=False)
    category: Mapped[str]
    status: Mapped[VerificationStatus] = mapped_column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    handled_by: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=True)
    admin_notes: Mapped[str] = mapped_column(nullable=True)
    seen: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    handler = relationship("AdminProfile", back_populates="verification_handled")
