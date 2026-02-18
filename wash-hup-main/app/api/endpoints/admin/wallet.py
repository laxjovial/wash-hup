from fastapi import APIRouter, status, HTTPException, Query
from ...dependencies import admin_dependency, db_dependency
from app.models.client.payment import Payment
from app.models.washer.transaction import Transaction, Remittance
from app.models.washer.profile import Wallet, WasherProfile
from sqlalchemy import func
from typing import Optional


router = APIRouter(
    prefix="/wallet",
    tags=["Admin: Wallet"]
)

@router.get("/overview", status_code=status.HTTP_200_OK)
async def get_wallet_overview(db: db_dependency, admin: admin_dependency):
    total_payments_count = db.query(Payment).filter(Payment.status == 'completed').count()
    total_payments_amount = db.query(func.sum(Payment.amount)).filter(Payment.status == 'completed').scalar() or 0.0

    total_remittance_amount = db.query(func.sum(Remittance.amount)).scalar() or 0.0

    return {
        "status": "success",
        "data": {
            "total_payments_count": total_payments_count,
            "total_payments_amount": total_payments_amount,
            "total_remittance_amount": total_remittance_amount,
            "platform_earnings": total_payments_amount - total_remittance_amount
        }
    }

@router.get("/payments", status_code=status.HTTP_200_OK)
async def get_payment_history(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return {"status": "success", "data": payments}

@router.get("/transactions", status_code=status.HTTP_200_OK)
async def get_transaction_history(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return {"status": "success", "data": transactions}

@router.get("/remittance", status_code=status.HTTP_200_OK)
async def get_remission_history(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    remittances = db.query(Remittance).offset(skip).limit(limit).all()
    return {"status": "success", "data": remittances}

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_wallet(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")

    wallet = db.query(Wallet).filter(Wallet.washer_id == washer.id).first()
    if not wallet:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    return {"status": "success", "data": wallet}

@router.get("/users/{user_id}/payments", status_code=status.HTTP_200_OK)
async def get_user_payments(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if profile:
        payments = db.query(Payment).filter(Payment.receiver_id == profile.id).all()
    else:
        from app.models.client.profile import OwnerProfile
        profile = db.query(OwnerProfile).filter(OwnerProfile.user_id == user_id).first()
        if not profile:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        payments = db.query(Payment).filter(Payment.sender_id == profile.id).all()

    return {"status": "success", "data": payments}

@router.get("/users/{user_id}/remission", status_code=status.HTTP_200_OK)
async def get_user_remission(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")

    remittances = db.query(Remittance).filter(Remittance.washer_id == washer.id).all()
    return {"status": "success", "data": remittances}
