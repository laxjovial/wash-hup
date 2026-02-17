from .base import BaseHandler
from app.crud.issues import create_issue_message
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket

class IssueHandler(BaseHandler):
    async def handle(self, msg, profile, ws: WebSocket, db: AsyncSession, manager):
        if profile.user_role == 'admin':
            await ws.send_json({"action": "notification", "sender": "system", "message": "invalid permission"})
            return 
        
        result = await create_issue_message(db, profile, msg["message"])
        if result in ("issue_error", "invalid_body"):
            await ws.send_json({"action": "notification", "sender": "system", "message": result})
            return

        data = {
            "action": "issue",
            "sender": profile.user.email,
            "fullname": profile.user.fullname,
            "time": str(result["data"].created),
            "message": msg["message"],
        }
        await ws.send_json(data)

        data.update({"issue_id": result["data"].issue_id})
        await manager.publish_to_admins(data)
    