# app/websocket/router.py
import asyncio
import json
from fastapi import APIRouter, Request, WebSocket, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.websocket.manager import WSManager, Channel, Role
from app.websocket.schema import validate
from app.websocket.handlers import get_handler
from app.api.dependencies import db_dependency, get_profile_model, redis_dependency
from app.core.security import get_user_from_token

router = APIRouter(prefix="/ws", tags=["websocket"])
template = Jinja2Templates(directory="app/template")

@router.get("/", response_class=HTMLResponse)
async def websocket_test(request: Request):
   return template.TemplateResponse("websocket.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def websocket_test(request: Request):
   return template.TemplateResponse("admin.html", {"request": request})

manager = WSManager()

@router.websocket("/connect/")
async def ws_endpoint(websocket: WebSocket, token: str, db: db_dependency, r: redis_dependency):
    # ---- Auth ----
    try:
        user = get_user_from_token(token)
    except:
        await websocket.close(code=1003, reason="invalid token")
        return

    profile = get_profile_model(db, user["id"])
    if not profile:
        await websocket.close(code=1003, reason="invalid user")
        return

    profile_id = str(profile.id)

    if r is None:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Offline mode: chat disabled"})
        await websocket.close(code=1013)  # Temporary unavailability
        return
    
    await manager.connect(profile_id, profile.user_role, websocket)

    channels = [Channel.ALL]
    role = profile.user_role

    if role == Role.OWNER:
        channels.extend([Channel.OWNERS, Channel.OWNERS_WASHERS])
    elif role == Role.WASHER:
        channels.extend([Channel.WASHERS, Channel.OWNERS_WASHERS])
    elif role == Role.ADMIN:
        channels.append(Channel.ADMINS)

    async def redis_listener():
        pubsub = r.pubsub()
        await pubsub.subscribe(*channels)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    data = json.loads(message["data"])
                    await websocket.send_json(data)
                except:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(*channels)
            await pubsub.close()
    
    # Start listening to Redis in background
    asyncio.create_task(redis_listener())

    try:
        while True:
            raw = await websocket.receive_text()
            data = validate(raw)

            if data is None:
                await websocket.send_json({"type": "error", "message": "No action."})
                continue

            handler = get_handler(data["action"])
            if not handler:
                await websocket.send_json({"type": "error", "message": "unknown action"})
                continue

            # ---- Dispatch ----
            await handler.handle(data, profile, websocket, db, manager)


    except WebSocketDisconnect:
        manager.disconnect(profile_id)
        await manager.publish(Channel.ALL, {
            "sender": "system",
            "text": f"{profile.user.fullname} left"
        })