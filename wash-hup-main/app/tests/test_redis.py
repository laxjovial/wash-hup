import asyncio
import redis.asyncio as redis

async def test():
    url = "redis://default:fhRJ2BQZGNLN8vdTCvm1iJvUz8fUKGu6@redis-18623.c338.eu-west-2-1.ec2.cloud.redislabs.com:18623"
    r = redis.from_url(url, decode_responses=True)
    try:
        print(f"PING: {r}", await r.ping())
    finally:
        await r.aclose()

asyncio.run(test())