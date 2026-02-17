from app.core.security import get_current_user, get_admin_user, get_washer_user, get_owner_user
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated
from app.models.auth.user import Profile
from fastapi import HTTPException
from app.services.redis import get_redis_client 
import redis.asyncio as redis

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
admin_dependency = Annotated[dict, Depends(get_admin_user)]
washer_dependency = Annotated[dict, Depends(get_washer_user)]
client_dependency = Annotated[dict, Depends(get_owner_user)]
redis_dependency = Annotated[redis.Redis, Depends(get_redis_client)]


# get profile model
def get_profile_model(db, id):
    profile = db.query(Profile).filter(Profile.user_id == id).first()

    if not profile:
        raise HTTPException(401, 'user profile not found')
    
    return profile

# def get_washer_profile_model(db, id):
#     profile = get_profile_model(db, id)

#     if profile.user_role != 'washer':
#         raise HTTPException(401, 'user is not a washer')
    
#     return profile


from collections import defaultdict
from fastapi import Request
from app.core.security import get_user_from_token
import time


# update to redis
user_rate_limits = defaultdict(list)
# user_rate_limits: dict[None, list] = {}
RATE_LIMIT = 10
RATE_PERIOD = 3600  # seconds (1 hour)

async def rate_limiter(request: Request):
    # Identify user by email if authenticated, else by IP
    user_id = None
    if "authorization" in request.headers:
        token = request.headers.get("authorization").replace("Bearer ", "")
        user = None
        try:
            user = get_user_from_token(token)
        except Exception:
            pass
        if user and "email" in user:
            user_id = user["email"]
    if not user_id:
        user_id = request.client.host

    now = time.time()
    # Remove timestamps older than RATE_PERIOD
    user_rate_limits[user_id] = [
        ts for ts in user_rate_limits[user_id] if now - ts < RATE_PERIOD
    ]
    if len(user_rate_limits[user_id]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Max 10 requests per hour."
        )
    user_rate_limits[user_id].append(now)


limit_dependency = Depends(rate_limiter)



# Problem 1 (Intern/SDE-1):
# "Design a rate limiter that allows 100 requests per user per hour"
# 
# Problem 2 (SDE-2):
# "Implement a cache with TTL that can handle 10k ops/sec"