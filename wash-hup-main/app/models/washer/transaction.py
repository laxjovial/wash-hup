from app.database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    wash_id: Mapped[str] = mapped_column(ForeignKey('washes.id'), nullable=False)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'), nullable=False)
    washer_name: Mapped[str]

    amount: Mapped[float]
    address: Mapped[str]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))


class Remittance(Base):
    __tablename__ = 'remittances'

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    Transaction_id: Mapped[str] = mapped_column(ForeignKey('transactions.id'), nullable=False)
    washer_id: Mapped[str] = mapped_column(ForeignKey('washer_profile.id'), nullable=False)
    amount: Mapped[float]
    charge: Mapped[float]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
