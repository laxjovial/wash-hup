from fastapi import APIRouter, status
from ...dependencies import db_dependency, washer_dependency, get_profile_model
from app.models.washer.profile import Wallet
from app.models.auth.user import Address
import json


router = APIRouter(
    prefix='/profile',
    tags=["Washer: Profile"]
)

@router.get('/', status_code=status.HTTP_200_OK)
async def get_profile(db: db_dependency, washer: washer_dependency):
    profile_model = get_profile_model(db, washer.get('id'))
    address = db.query(Address).filter(Address.profile_id == profile_model.id).first()
    wallet_model = db.query(Wallet).filter(Wallet.washer_id == profile_model.id).first()
    

    data = {
            "wallet": wallet_model.balance if wallet_model else 0.00,
            "remittance": 450.00,
            "rating": 1.0,
            "fullname": profile_model.user.fullname,
            "email": profile_model.user.email,
            "phone_number": profile_model.user.phone_number,
            "profile_pic": profile_model.profile_image,
            "is_verified": profile_model.profile_verified,
            "location": address.address1 if address else None,
            "is_available": profile_model.available
        }
    
    return {
        "message": "profile retrieved successfully",
        "status": "ok",
        "data": data
    }
