from app.database import Base
from sqlalchemy import Column, String, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from enum import Enum
from app.models.admin.profile import AdminProfile


reward_washers = Table(
    "reward_washers",
    Base.metadata,
    Column("reward_id", String, ForeignKey("rewards.id"), primary_key=True),
    Column("washer_id", String, ForeignKey("reward_requests.id"), primary_key=True)
)

class RewardStatus(str, Enum):
    PENDING = 'pending'
    ACHIEVED = 'achieved'
    CLAIMED = 'claimed'

class Reward(Base):
    __tablename__ = "rewards"

    id: Mapped[str] = mapped_column(primary_key=True, index=True) 

    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)
    title: Mapped[str]
    rating: Mapped[float]
    expiry_date: Mapped[datetime]
    available: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    achievers: Mapped[list["RewardRequest"]] = relationship("RewardRequest", secondary=reward_washers, back_populates="rewards")

class RewardRequest(Base):
    __tablename__ = "reward_requests"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    washer_id: Mapped[str] = mapped_column(ForeignKey("washer_profile.id"))
    reward_id: Mapped[str] = mapped_column(ForeignKey("rewards.id"))

    status: Mapped[RewardStatus] = mapped_column(SQLEnum(RewardStatus), default=RewardStatus.PENDING)
    address: Mapped[str]
    city: Mapped[str]
    state: Mapped[str]
    phone_number: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    rewards: Mapped[list["Reward"]] = relationship("Reward", secondary=reward_washers, back_populates="achievers")



class Discounts(Base):
    __tablename__ = 'discounts'

    id: Mapped[str] = mapped_column(primary_key=True, index=True) 
    profile_id: Mapped[str] = mapped_column(ForeignKey('profile.id'), unique=True, nullable=False)
    admin_id: Mapped[str] = mapped_column(ForeignKey('admin_profile.id'), nullable=False)

    title: Mapped[str]
    description: Mapped[str] 
    progress: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    is_available: Mapped[bool] = mapped_column(default=True)
    collected: Mapped[bool] = mapped_column(default=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    creator: Mapped["AdminProfile"] = relationship("AdminProfile", back_populates="discounts")
