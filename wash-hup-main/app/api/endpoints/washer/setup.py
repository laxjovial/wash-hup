from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from ...dependencies import db_dependency, get_profile_model, washer_dependency, redis_dependency
from app.models.auth.user import Address
from app.services.paystack import create_subaccount
from app.models.washer.profile import Wallet, WasherProfile
from app.models.admin.profile import VerificationRequest
from app.schemas.request.washer import AccountDetailRequest
from app.services.paystack import get_bank_list
from uuid import uuid4
import json

# todo
# 1. add email notificaton and push notification 


router = APIRouter(
    prefix="",
    tags=["Washer: Profile Setup"]
)

@router.patch('/availability', status_code=status.HTTP_200_OK)
async def update_washer_availability(db: db_dependency, r: redis_dependency, washer: washer_dependency, available: bool):
    profile_model = db.query(WasherProfile).filter(WasherProfile.user_id == washer.get('id')).first()

    if not profile_model:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile_model.user_role != "washer":
        raise HTTPException(status_code=400, detail="Invalid user role")

    if available:
        address = db.query(Address).filter(Address.profile_id == profile_model.id).first()

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
        
        point = db.scalar(select(func.ST_AsText(Address.geom)).where(Address.id == address.id))
        longitude = float(point.split('(')[1].split(' ')[0])
        latitude = float(point.split(' ')[1].split(')')[0])
        
        await r.geoadd("washers:location", (longitude, latitude, profile_model.id))

        profile_model.available = True
        db.commit()
        db.refresh(profile_model)

        return {
            "message": "washer availability updated successfully",
            "status": "ok",
        }

    await r.zrem("washers:location", profile_model.id)
    profile_model.available = False
    db.commit()
    
    return {
        "message": "washer unavailability updated successfully",
        "status": "ok"
    }

@router.post('/account-detail', status_code=status.HTTP_201_CREATED)
async def add_payment_destination(
    request: AccountDetailRequest, 
    db: db_dependency, 
    washer: washer_dependency,
):
    profile_model = get_profile_model(db, washer.get('id'))
    wallet_model = db.query(Wallet).filter(Wallet.washer_id == profile_model.id).first()

    if wallet_model:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "payment account already added")

    wallet = await create_subaccount(
        fullname=request.account_name,
        bank_code=request.bank_code,
        account_number=request.account_number,
        charge=10
    )

    if not wallet["status"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, wallet["message"])
    
    wallet_data = wallet.get("data")
    wallet_model = Wallet(
        id=wallet_data["subaccount_code"],
        account_name=wallet_data["account_name"],
        bank_name=wallet_data["settlement_bank"],
        washer_id=profile_model.id,
        account_number=request.account_number,
        bank_code=request.bank_code
    )

    db.add(wallet_model)
    db.commit()

    data = {
        "account_name": wallet_data["account_name"],
        "account_number": wallet_data["account_number"],
        "bank_name": wallet_data["settlement_bank"],
    }

    return {
        "message": "payment account added successfully",
        "status": "ok",
        "data": data
    }

@router.get("/bank-list", status_code=status.HTTP_200_OK)
async def get_list_of_banks(washer: washer_dependency, r: redis_dependency):
    bank_list = await r.getex("bank-list")

    if not bank_list:
        bank_list = await get_bank_list()
        await r.setex("bank-list", 3600*24, json.dumps(bank_list))

        return {
            "message": "bank list retrieved successfully",
            "status": "ok",
            "data": bank_list
        }

    return {
            "message": "bank list retrieved successfully",
            "status": "ok",
            "data": json.loads(bank_list)
        }

#manual verification
@router.post('/verify-account', status_code=status.HTTP_202_ACCEPTED)
async def verify_account(db: db_dependency, washer: washer_dependency):
    profile_model = get_profile_model(db, washer.get('id'))

    if profile_model.profile_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already verified")
    
    verification = db.query(VerificationRequest).filter(VerificationRequest.washer_id == profile_model.id).first()

    if verification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile verification already sent.")
    
    request_model = VerificationRequest(
        id="vr_"+str(uuid4()),
        washer_id=profile_model.id,
        category="Profile Verification"
    )
    db.add(request_model)
    db.commit()
    # send email 
    return {
        "message": "Profile verification sent successfully, please check your email.",
        "status": "ok"
    }


    # send email
    return {
        "message": "nin verified successfully",
        "status": "ok"
    }