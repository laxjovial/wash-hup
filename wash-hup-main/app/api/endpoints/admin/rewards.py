from fastapi import APIRouter, status, HTTPException, Body
from ...dependencies import admin_dependency, db_dependency, get_profile_model
from app.models.admin.rewards import Reward, RewardRequest, Discounts
from app.models.washer.profile import WasherProfile
from app.schemas.request.admin import RewardCreateSchema, DiscountCreateSchema
from app.schemas.response.admin import AdminBaseResponse, AdminDataResponse
from uuid import uuid4
from datetime import datetime
from typing import Optional


router = APIRouter(
    prefix="/rewards",
    tags=["Admin: Rewards & Discounts"]
)

@router.get("", status_code=status.HTTP_200_OK, response_model=AdminDataResponse)
async def get_rewards(db: db_dependency, admin: admin_dependency):
    rewards = db.query(Reward).all()
    return {"status": "success", "data": rewards}

@router.post("", status_code=status.HTTP_201_CREATED, response_model=AdminBaseResponse)
async def create_reward(
    db: db_dependency,
    admin: admin_dependency,
    data: RewardCreateSchema
):
    profile = get_profile_model(db, admin.get("id"))
    reward = Reward(
        id="rew_"+str(uuid4()),
        admin_id=profile.id,
        title=data.title,
        rating=data.rating_required,
        expiry_date=data.expiry_date
    )
    db.add(reward)
    db.commit()
    db.refresh(reward)
    return {"status": "success", "data": reward}

@router.get("/requests", status_code=status.HTTP_200_OK)
async def get_reward_requests(db: db_dependency, admin: admin_dependency):
    requests = db.query(RewardRequest).all()
    return {"status": "success", "data": requests}

@router.get("/discounts", status_code=status.HTTP_200_OK)
async def get_all_discounts(db: db_dependency, admin: admin_dependency):
    discounts = db.query(Discounts).all()
    return {"status": "success", "data": discounts}

@router.post("/discounts", status_code=status.HTTP_201_CREATED, response_model=AdminBaseResponse)
async def create_discount(
    db: db_dependency,
    admin: admin_dependency,
    data: DiscountCreateSchema
):
    from app.models.auth.user import Profile
    user_profile = db.query(Profile).filter(Profile.user_id == data.user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    discount = Discounts(
        id="disc_"+str(uuid4()),
        profile_id=user_profile.id,
        title=data.title,
        description=data.description,
        total=data.total
    )
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return {"status": "success", "data": discount}
