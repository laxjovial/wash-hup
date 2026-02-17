from fastapi import APIRouter, status
from ...dependencies import admin_dependency, db_dependency, redis_dependency
from app.models.admin.prices import ServicePrice
from uuid import uuid4


router = APIRouter(
    prefix="/accounts",
    tags=["Admin: Accounts Management"]
)

@router.get("/owners", status_code=status.HTTP_200_OK)
async def get_owner_accounts():
    pass

@router.get("/owners/filter", status_code=status.HTTP_200_OK)
async def filter_owner_accounts():
    pass

@router.get("/owners/{user_id}", status_code=status.HTTP_200_OK)
async def get_owner_account():
    pass

@router.get("/washers", status_code=status.HTTP_200_OK)
async def get_washer_accounts():
    pass

@router.get("/washers/filter", status_code=status.HTTP_200_OK)
async def filter_washer_accounts():
    pass

@router.get("/washers/{user_id}", status_code=status.HTTP_200_OK)
async def get_washer_account():
    pass

@router.get("/verifications", status_code=status.HTTP_200_OK)
async def get_verification_accounts():
    pass

@router.get("/verifications/filter", status_code=status.HTTP_200_OK)
async def filter_verification_accounts():
    pass

@router.post("/verifications/accept/{user_id}", status_code=status.HTTP_200_OK)
async def accept_verification_account():
    pass

@router.post("/verifications/reject/{user_id}", status_code=status.HTTP_200_OK)
async def reject_verification_account():
    pass

@router.post("/verifications/resubmit/{user_id}", status_code=status.HTTP_200_OK)
async def resubmit_verification_account():
    pass

@router.get("/verifications/{user_id}", status_code=status.HTTP_200_OK)
async def get_verification_account():
    pass

@router.post("/restrict/{user_id}", status_code=status.HTTP_200_OK)
async def restrict_account():
    pass

@router.post("/deactivate/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_account():
    pass

@router.post("/flag/{user_id}", status_code=status.HTTP_200_OK)
async def flag_account():
    pass

@router.post("/activate/{user_id}", status_code=status.HTTP_200_OK)
async def activate_account():
    pass

@router.post("/unrestrict/{user_id}", status_code=status.HTTP_200_OK)
async def unrestrict_account():
    pass

@router.post("/unflag/{user_id}", status_code=status.HTTP_200_OK)
async def unflag_account():
    pass