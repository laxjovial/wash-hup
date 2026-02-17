from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone 
from app.database import Base


class ServicePrice(Base):
    __tablename__ = "service_price"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(ForeignKey("admin_profile.id"), nullable=False)
    quick_min: Mapped[float]
    quick_max: Mapped[float]
    smart_min: Mapped[float]
    smart_max: Mapped[float]
    premium_min: Mapped[float]
    premium_max: Mapped[float]
    created: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
