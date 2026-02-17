from app.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from ..auth.user import Profile


class OwnerProfile(Profile):
    __tablename__ = 'owner_profile'

    id: Mapped[str] = mapped_column(ForeignKey('profile.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'owner'
    }

