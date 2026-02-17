from fastapi import APIRouter, status, HTTPException, Query
from ...dependencies import db_dependency, washer_dependency, get_profile_model, redis_dependency
from app.models.client.wash import Review
from app.models.admin.rewards import Reward, RewardRequest
from app.schemas.request.washer import RewardRequestSchema
from typing import Literal
from uuid import uuid4
import json


router = APIRouter(
    prefix="/rating",
    tags=["Washer: Rating and rewards"]
)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_ratings_history(
    db: db_dependency,
    washer: washer_dependency,
    skip: int = 0,
    limit: int = 10
):
    profile_model = get_profile_model(db, washer.get("id"))
    reviews = db.query(Review).filter(Review.washer_id == profile_model.id).offset(skip).limit(limit).all()

    return {
        "message": "Rating and reviews retrieved successfully",
        "status": "ok",
        "data": reviews
    }

@router.get("/chart-data", status_code=status.HTTP_200_OK)
async def get_rating_chart_data(
    db: db_dependency,
    washer: washer_dependency,
    redis: redis_dependency,
    filter: Literal["week", "month", "last_month", "3_months"] = "week"
):
    profile_model = get_profile_model(db, washer.get("id"))
    # time filter 
    reviews = db.query(Review).filter(Review.washer_id == profile_model.id).all()
    
    if not reviews:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No reviews found")
    
    return {
        "message": "incomplete endpoint, check in later",
        "status": "incomplete",
        "data": None
    }
        
@router.get("/available-rewards", status_code=status.HTTP_200_OK)
async def get_available_rewards(
    db: db_dependency,
    washer: washer_dependency,
    redis: redis_dependency
):
    profile_model = get_profile_model(db, washer.get("id"))
    rewards = db.query(Reward).join(Reward.achievers).filter(RewardRequest.washer_id != profile_model.id).all()

    return {
        "message": "Rewards retrieved successfully",
        "status": "ok",
        "data": rewards
    }

@router.get("/claimed-rewards", status_code=status.HTTP_200_OK)
async def claim_reward(
    db: db_dependency,
    washer: washer_dependency,
    redis: redis_dependency
):
    profile_model = get_profile_model(db, washer.get("id"))

    rewards = db.query(Reward).join(Reward.achievers).filter(RewardRequest.washer_id == profile_model.id).all()
    
    return {
        "message": "Rewards retrieved successfully",
        "status": "ok",
        "data": rewards
    }

@router.post("/claim-reward", status_code=status.HTTP_201_CREATED)
async def claim_reward(
    db: db_dependency,
    washer: washer_dependency,
    form: RewardRequestSchema
):
    profile_model = get_profile_model(db, washer.get("id"))

    reward_model = db.query(Reward).filter(Reward.id == form.reward_id).first()

    if not reward_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reward not found")
    
    if reward_model.available == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reward not available")
    
    reward_request = db.query(RewardRequest).filter(RewardRequest.reward_id == reward_model.id, RewardRequest.washer_id == profile_model.id).first()

    if reward_request:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reward already claimed")
    
    reward_request = RewardRequest(
        id=str(uuid4()),
        reward_id=reward_model.id,
        washer_id=profile_model.id,
        address=form.address,
        city=form.city,
        state=form.state,
        phone_number=form.phone_number
    )

    db.add(reward_request)
    db.commit()
    db.refresh(reward_request)

    return {
        "message": "Reward claimed successfully",
        "status": "ok",
        "data": reward_request
    }

