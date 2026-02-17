from fastapi import APIRouter, status
from ...dependencies import db_dependency, washer_dependency, get_profile_model
from app.models.washer.transaction import Remittance, Transaction
import json


router = APIRouter(
    prefix="/wallet",
    tags=["Washer: Wallet"]
)

@router.get("/earnings")
async def get_earning_history(
    db: db_dependency, 
    washer: washer_dependency,
    skip: int = 0, 
    limit: int = 10
):
    profile_model = get_profile_model(db, washer.get("id"))
    trancactions = db.query(Transaction).filter(Transaction.washer_id == profile_model.id).offset(skip).limit(limit).all()

    return {
        "message": "transactions retrieved successfully",
        "status": "ok",
        "data": trancactions
    }


@router.get("/remittance")
async def get_remittance_history(
    db: db_dependency, 
    washer: washer_dependency,
    skip: int = 0, 
    limit: int = 10
):
    profile_model = get_profile_model(db, washer.get("id"))
    remittances = db.query(Remittance).filter(Remittance.washer_id == profile_model.id).offset(skip).limit(limit).all()

    return {
        "message": "remittances retrieved successfully",
        "status": "ok",
        "data": remittances
    }



