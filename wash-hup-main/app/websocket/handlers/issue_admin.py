from .base import BaseHandler
from app.crud.issues import create_issue_message_admin
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket

class IssueAdminHandler(BaseHandler):
    async def handle(self, msg, profile, ws: WebSocket, db: AsyncSession, manager):
        if profile.user_role != 'admin':
            await ws.send_json({"action": "notification", "sender": "system", "message": "invalid permission"})
            return 
        
        # Logic to handle admin responding to user issues via WebSocket
        result = await create_issue_message_admin(db, profile, msg)

        if result == "issue_error":
            await ws.send_json({"action": "notification", "sender": "system", "message": "Issue not found"})
            return
        elif result == "invalid_message":
            await ws.send_json({"action": "notification", "sender": "system", "message": "Invalid message body"})
            return
        elif isinstance(result, str):
             await ws.send_json({"action": "notification", "sender": "system", "message": result})
             return

        data = {
            "action": "issue",
            "issue_id": result["data"].issue_id,
            "sender": profile.user.email,
            "fullname": profile.user.fullname,
            "time": str(result["data"].created),
            "message": msg["message"],
        }

        # Send confirmation to admin
        await ws.send_json(data)

        # send to issue owner (the client or washer who reported it)
        user_message = data.copy()
        user_message.pop("issue_id")
        await manager.send_personal(user_message, result["owner_id"])
        
    