from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks
from ...dependencies import db_dependency, client_dependency, get_profile_model, redis_dependency
from app.models.client.payment import Payment
from app.models.admin.rewards import Discounts
from app.schemas.request.client import ProfileUpdateRequest
from app.schemas.response.client import ProfileResponse
from app.core.security import bcrypt_context
from app.crud.notifications import NOTIFICATION, NOTIFY
import json



router = APIRouter(
    prefix='/profile',
    tags=['Car owners: profile']
)


@router.get('/', status_code=200, response_model=ProfileResponse)
async def get_profile(db: db_dependency, user: client_dependency, r: redis_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    profile = await r.get("profile_"+profile_model.id)

    if not profile:
        data = {
            "fullname": profile_model.user.fullname,
            "email": profile_model.user.email,
            "phone_number": profile_model.user.phone_number,
            "payment_method": profile_model.payment_method,
            "profile_pic": profile_model.profile_image,
            "is_restricted": profile_model.is_restricted,
            "is_flagged": profile_model.is_flagged
        }
        await r.setex("profile_"+profile_model.id, 24*3600, json.dumps(data))

        return {
            "message": "profile retrieved successfully",
            "status": "ok",
            "data": data
        }
    
    return {
        "message": "profile retrieved successfully",
        "status": "ok",
        "data": json.loads(profile)
    }

@router.put('/', status_code=200, response_model=ProfileResponse)
async def update_profile(profile_data: ProfileUpdateRequest, db: db_dependency, user: client_dependency, bgtask: BackgroundTasks):
    profile_model = get_profile_model(db, user.get('id'))

    if not bcrypt_context.verify(profile_data.password, profile_model.user.hashed_password):
        raise HTTPException(status_code=401, detail="incorrect password")
    
    if profile_model.updated + timedelta(days=14) > datetime.now():
        # add timezone later
        raise HTTPException(status_code=403, detail="profile can only be updated once in 14 days")
    
    if profile_data.fullname:
        profile_model.user.fullname = profile_data.fullname
    if profile_data.email:
        profile_model.user.email = profile_data.email
    if profile_data.phone_number:
        profile_model.user.phone_number = profile_data.phone_number

    db.add(profile_model)
    db.commit()
    db.refresh(profile_model)

    bgtask.add_task(NOTIFY.create, db, profile_model.id, "Profile updated", NOTIFICATION.profile_update, fullname=profile_model.user.fullname)


    data = {
        "fullname": profile_model.user.fullname,
        "email": profile_model.user.email,
        "phone_number": profile_model.user.phone_number,
        "payment_method": profile_model.payment_method,
        "profile_pic": profile_model.profile_image,
        "is_restricted": profile_model.is_restricted,
        "is_flagged": profile_model.is_flagged
    }
    return {
        "message": "profile updated successfully",
        "status": "ok",
        "data": data
    }

# Transactions Requests
@router.get('/transactions', status_code=200) #, response_model=TransactionResponse)
async def get_transactions(db: db_dependency, user: client_dependency, skip: int = 0, limit: int = 10):
    profile_model = get_profile_model(db, user.get('id'))
    transactions = db.query(Payment).filter(Payment.sender_id == profile_model.id).order_by(Payment.created.desc()).offset(skip).limit(limit).all()

    return {
        "message": "transactions retrieved successfully",
        "status": "ok",
        "data": transactions
    }

# Discount
@router.get('/discounts')
async def get_discounts(db: db_dependency, user: client_dependency, skip: int = 0, limit: int = 10):
    profile_model = get_profile_model(db, user.get('id'))
    discounts = db.query(Discounts).filter(Discounts.profile_id == profile_model.id).order_by(Discounts.created.desc()).offset(skip).limit(limit).all()

    return {
        "message": "discounts retrieved successfully",
        "status": "ok",
        "data": discounts
    }