# app/redis.py
import os
import redis.asyncio as redis
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

_pool: redis.ConnectionPool | None = None

async def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        if REDIS_URL:
            _pool = redis.ConnectionPool.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
        else:
            _pool = redis.ConnectionPool(
                host=REDIS_HOST,
                port=int(REDIS_PORT),
                password=os.getenv("REDIS_PASSWORD"),
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
