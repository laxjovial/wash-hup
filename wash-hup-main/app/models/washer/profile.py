from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from ..auth.user import Profile



class WasherProfile(Profile):
    __tablename__ = 'washer_profile'

    id: Mapped[str] = mapped_column(ForeignKey('profile.id'), primary_key=True, index=True)
    rating: Mapped[float] = mapped_column(default=0.0)
    total_washes: Mapped[int] = mapped_column(default=0)
    available: Mapped[bool] = mapped_column(default=False)
    nin_verified: Mapped[bool] = mapped_column(default=False)
    profile_verified: Mapped[bool] = mapped_column(default=False) # manual verification 

    wallet = relationship("Wallet", back_populates="washer", uselist=False, cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_identity': 'washer'
    }

class Wallet(Base):
    __tablename__ = 'wallet'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'))
    balance: Mapped[float] = mapped_column(default=0.00)

    account_number: Mapped[str]
    account_name: Mapped[str]
    bank_name: Mapped[str]
    bank_code: Mapped[str]

    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated: Mapped[datetime] = mapped_column(default=None, onupdate=datetime.now(timezone.utc))

    washer = relationship("WasherProfile", back_populates="wallet")