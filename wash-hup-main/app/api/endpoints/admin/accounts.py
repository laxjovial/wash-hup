from fastapi import APIRouter, status, HTTPException, Query, Body

from ...dependencies import admin_dependency, db_dependency
from app.models.auth.user import User, Profile
from app.models.client.profile import OwnerProfile
from app.models.washer.profile import WasherProfile
from app.models.admin.profile import VerificationRequest
from app.crud.notifications import NOTIFY, NOTIFICATION

from uuid import uuid4
from typing import Optional


router = APIRouter(
    prefix="/accounts",
    tags=["Admin: Accounts Management"]
)

@router.get("/owners", status_code=status.HTTP_200_OK)
async def get_owner_accounts(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    owners = db.query(OwnerProfile).offset(skip).limit(limit).all()
    return {"status": "success", "data": owners}

@router.get("/owners/filter", status_code=status.HTTP_200_OK)
async def filter_owner_accounts(db: db_dependency, admin: admin_dependency, fullname: Optional[str] = None):
    query = db.query(OwnerProfile).join(User)
    if fullname:
        query = query.filter(User.fullname.ilike(f"%{fullname}%"))
    owners = query.all()
    return {"status": "success", "data": owners}

@router.get("/owners/{user_id}", status_code=status.HTTP_200_OK)
async def get_owner_account(user_id: str, db: db_dependency, admin: admin_dependency):
    owner = db.query(OwnerProfile).filter(OwnerProfile.user_id == user_id).first()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner account not found")
    return {"status": "success", "data": owner}

@router.get("/washers", status_code=status.HTTP_200_OK)
async def get_washer_accounts(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    washers = db.query(WasherProfile).offset(skip).limit(limit).all()
    return {"status": "success", "data": washers}

@router.get("/washers/filter", status_code=status.HTTP_200_OK)
async def filter_washer_accounts(db: db_dependency, admin: admin_dependency, fullname: Optional[str] = None):
    query = db.query(WasherProfile).join(User)
    if fullname:
        query = query.filter(User.fullname.ilike(f"%{fullname}%"))
    washers = query.all()
    return {"status": "success", "data": washers}

@router.get("/washers/{user_id}", status_code=status.HTTP_200_OK)
async def get_washer_account(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer account not found")
    return {"status": "success", "data": washer}

@router.get("/verifications", status_code=status.HTTP_200_OK)
async def get_verification_accounts(db: db_dependency, admin: admin_dependency):
    verifications = db.query(VerificationRequest).all()
    return {"status": "success", "data": verifications}

@router.get("/verifications/filter", status_code=status.HTTP_200_OK)
async def filter_verification_accounts(db: db_dependency, admin: admin_dependency, seen: Optional[bool] = None):
    query = db.query(VerificationRequest)
    if seen is not None:
        query = query.filter(VerificationRequest.seen == seen)
    verifications = query.all()
    return {"status": "success", "data": verifications}

@router.post("/verifications/accept/{user_id}", status_code=status.HTTP_200_OK)
async def accept_verification_account(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")
    washer.profile_verified = True

    # Mark verification request as seen
    req = db.query(VerificationRequest).filter(VerificationRequest.washer_id == washer.id).first()
    if req:
        req.seen = True

    db.commit()
    return {"status": "success", "message": "Verification accepted"}

@router.post("/verifications/reject/{user_id}", status_code=status.HTTP_200_OK)
async def reject_verification_account(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")
    washer.profile_verified = False

    req = db.query(VerificationRequest).filter(VerificationRequest.washer_id == washer.id).first()
    if req:
        req.seen = True

    db.commit()
    return {"status": "success", "message": "Verification rejected"}

@router.post("/verifications/resubmit/{user_id}", status_code=status.HTTP_200_OK)
async def resubmit_verification_account(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")

    # Reset verification status and mark request for resubmission
    washer.profile_verified = False
    req = db.query(VerificationRequest).filter(VerificationRequest.washer_id == washer.id).first()
    if req:
        req.seen = True # Mark current request as handled
        # In a real app, you might create a new notification for the washer

    db.commit()
    return {"status": "success", "message": "Resubmit request handled"}

@router.get("/verifications/{user_id}", status_code=status.HTTP_200_OK)
async def get_verification_account(user_id: str, db: db_dependency, admin: admin_dependency):
    washer = db.query(WasherProfile).filter(WasherProfile.user_id == user_id).first()
    if not washer:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Washer profile not found")
    verification = db.query(VerificationRequest).filter(VerificationRequest.washer_id == washer.id).first()
    return {"status": "success", "data": verification}

@router.post("/restrict/{user_id}", status_code=status.HTTP_200_OK)
async def restrict_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_restricted = True
    db.commit()
    return {"status": "success", "message": "Account restricted"}

@router.post("/deactivate/{user_id}", status_code=status.HTTP_200_OK)
async def deactivate_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_deactivated = True
    db.commit()
    return {"status": "success", "message": "Account deactivated"}

@router.post("/flag/{user_id}", status_code=status.HTTP_200_OK)
async def flag_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_flagged = True
    db.commit()
    return {"status": "success", "message": "Account flagged"}

@router.post("/activate/{user_id}", status_code=status.HTTP_200_OK)
async def activate_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_deactivated = False
    db.commit()
    return {"status": "success", "message": "Account activated"}

@router.post("/unrestrict/{user_id}", status_code=status.HTTP_200_OK)
async def unrestrict_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_restricted = False
    db.commit()
    return {"status": "success", "message": "Account unrestricted"}

@router.post("/unflag/{user_id}", status_code=status.HTTP_200_OK)
async def unflag_account(user_id: str, db: db_dependency, admin: admin_dependency):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    profile.is_flagged = False
    db.commit()
    return {"status": "success", "message": "Account unflagged"}

@router.post("/{user_id}/notify", status_code=status.HTTP_201_CREATED)
async def send_user_notification(
    user_id: str,
    db: db_dependency,
    admin: admin_dependency,
    title: str = Body(..., embed=True),
    message: str = Body(..., embed=True)
):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    await NOTIFY.create(db, profile.id, title, message, fullname=profile.user.fullname)
    return {"status": "success", "message": "Notification sent"}

