# app/redis.py
import os
import redis.asyncio as redis
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

_pool: redis.ConnectionPool | None = None

async def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _pool

async def get_redis_client() -> redis.Redis:
    pool = await get_redis_pool()
    client = redis.Redis(connection_pool=pool)

    return client