from fastapi import APIRouter, status
from ...dependencies import admin_dependency, db_dependency, redis_dependency
from app.models.admin.prices import ServicePrice
from uuid import uuid4


router = APIRouter(
    prefix="/wallet",
    tags=["Admin: Wallet"]
)

@router.get("/overview", status_code=status.HTTP_200_OK)
async def get_overview():
    pass

@router.get("/filter", status_code=status.HTTP_200_OK)
async def get_overview():
    pass

@router.get("/payments", status_code=status.HTTP_200_OK)
async def get_wallet_history():
    pass

@router.get("/remission", status_code=status.HTTP_200_OK)
async def get_remission_history():
    pass

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_wallet():
    pass

@router.get("/users/{user_id}/payments", status_code=status.HTTP_200_OK)
async def get_user_payments():
    pass

@router.get("/users/{user_id}/remission", status_code=status.HTTP_200_OK)
async def get_user_remission():
    pass

