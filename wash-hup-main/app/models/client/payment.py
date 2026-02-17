from app.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey('owner_profile.id'), nullable=False)
    sender_name: Mapped[str]

    receiver_id: Mapped[int] = mapped_column(ForeignKey('washer_profile.id'), nullable=False)
    receiver_name: Mapped[str]

    wash_id: Mapped[int] = mapped_column(ForeignKey('washes.id'), nullable=False)

    reference: Mapped[str] = mapped_column(unique=True, nullable=False)
    amount: Mapped[float]
    status: Mapped[PaymentStatus] = mapped_column(default=None)

    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

