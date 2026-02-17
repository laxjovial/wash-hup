from abc import ABC, abstractmethod
from fastapi import WebSocket
from app.models.auth.user import Profile
from sqlalchemy.ext.asyncio import AsyncSession

class BaseHandler(ABC):
    @abstractmethod
    async def handle(
        self,
        msg: dict,
        profile: Profile,
        ws: WebSocket,
        db: AsyncSession,
        manager
    ) -> dict | None:
        """Return a dict to broadcast, or None to skip."""
        ...