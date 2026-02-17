# app/ws_manager.py
from fastapi import WebSocket
from typing import Dict
from app.services.redis import get_redis_client as get_redis
import json
import asyncio


class Role:
    OWNER = "owner"
    WASHER = "washer"
    ADMIN = "admin"

class Channel:
    ALL = "all"
    OWNERS = "owners"
    WASHERS = "washers"
    ADMINS = "admins"
    OWNERS_WASHERS = "owners_washers"


VALID_ROLES = [Role.OWNER, Role.WASHER, Role.ADMIN]

class WSManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

        self.owner_connections: set[str] = set()
        self.washer_connections: set[str] = set()
        self.admin_connections: set[str] = set()

        self.channels = [Channel.ALL, Channel.OWNERS, Channel.WASHERS, Channel.ADMINS, Channel.OWNERS_WASHERS]


    # ---- WebSocket lifecycle ----
    async def connect(self, profile_id: str, role: str, websocket: WebSocket):
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role: {role}")
        
        await websocket.accept()
        self.active_connections[profile_id] = websocket

        if role == Role.OWNER:
            self.owner_connections.add(profile_id)
        elif role == Role.WASHER:
            self.washer_connections.add(profile_id)
        elif role == Role.ADMIN:
            self.admin_connections.add(profile_id)


    def disconnect(self, profile_id: str):
        self.active_connections.pop(profile_id, None)
        self.owner_connections.discard(profile_id)
        self.washer_connections.discard(profile_id)
        self.admin_connections.discard(profile_id)

    async def send_personal(self, data: dict, profile_id: str):
        if websocket := self.active_connections.get(profile_id):
            await websocket.send_json(data)

    # send group message (local only)
    async def broadcast_to_owners(self, data: dict):
        for user_id in self.owner_connections:
            await self.send_personal(data, user_id)

    async def broadcast_to_washers(self, data: dict):
        for user_id in self.washer_connections:
            await self.send_personal(data, user_id)

    async def broadcast_to_owners_and_washers(self, data: dict):
        for user_id in self.owner_connections.union(self.washer_connections):
            await self.send_personal(data, user_id)

    async def broadcast_to_admins(self, data: dict):
        for user_id in self.admin_connections:
            await self.send_personal(data, user_id)

    async def broadcast_to_users(self, data: dict):
        for user_id in self.active_connections:
                await self.send_personal(data, user_id)

    
    # publish to redis (Global)
    async def publish_to_owners(self, data: dict):
        await self.publish(Channel.OWNERS, data)

    async def publish_to_washers(self, data: dict):
        await self.publish(Channel.WASHERS, data)

    async def publish_to_admins(self, data: dict):
        await self.publish(Channel.ADMINS, data)

    async def publish_to_all(self, data: dict):
        await self.publish(Channel.ALL, data)
    
    async def publish_to_owners_and_washers(self, data: dict):
        await self.publish(Channel.OWNERS_WASHERS, data)

    async def publish(self, channel: str, data: dict):
        """Push a message to Redis → every FastAPI worker receives it."""
        r = await get_redis()
        await r.publish(channel, json.dumps(data))