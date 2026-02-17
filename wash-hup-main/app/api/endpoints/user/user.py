from fastapi import APIRouter, UploadFile, HTTPException, status, BackgroundTasks
from app.models.admin.profile import Faqs, TermsAndConditions
from ...dependencies import db_dependency, get_profile_model, user_dependency, redis_dependency
from app.schemas.response.user import ProfileResponse
from app.schemas.request.auth import AddressSchema
from app.models.auth.user import Address
from app.models.washer.profile import Wallet
from geoalchemy2.functions import ST_GeomFromText
from app.models.auth.user import Notifications
from app.schemas.response.client import NotificationResponse 
from uuid import uuid4
from app.models.client.profile import Profile
from app.utils.upload_image import upload_pic
from app.schemas.response.client import FaqResponse
from app.crud.notifications import NOTIFY, NOTIFICATION
import json


router = APIRouter(
    prefix="/user",
    tags=["User"],
)

@router.get('/profile', status_code=status.HTTP_200_OK) #, response_model=ProfileResponse)
async def get_user_profile(db: db_dependency, user: user_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    address = db.query(Address).filter(Address.profile_id == profile_model.id).first()

    if profile_model.user_role == 'owner':
        data = {
            "user_id": profile_model.user.id,
            "fullname": profile_model.user.fullname,
            "profile_pic": profile_model.profile_image,
            "location": address.address1 if address else None
        }

    if profile_model.user_role == 'washer':
        wallet = db.query(Wallet).filter(Wallet.washer_id == profile_model.id).first()

        complete_profile = {
            "address": True if address else False,
            "profile_pic": True if profile_model.profile_image else False,
            "payment_detail": True if wallet else False,
            "availability": profile_model.available
        }
        data = {
            "user_id": profile_model.user.id,
            "fullname": profile_model.user.fullname,
            "profile_pic": profile_model.profile_image,
            "balance": wallet.balance if wallet else 0.00, # fix bal, remittance and rating
            "remittance": 3,
            "rating": 1.0,
            "is_verified": profile_model.profile_verified,
            "role": profile_model.user_role,
            "location": address.address1 if address else None,
            "complete_setup": complete_profile
        }

    return {
        "status": "ok",
        "message": "profile retreived successfully.",
        "data": data
    }

# Notification Requests
@router.get('/notification', status_code=status.HTTP_200_OK, response_model=NotificationResponse)
async def get_notifications(db: db_dependency, user: user_dependency, skip: int = 0, limit: int = 10):
    profile_model = get_profile_model(db, user.get('id'))
    notifications = db.query(Notifications).filter(Notifications.profile_id == profile_model.id, Notifications.is_read == False).order_by(Notifications.created.desc()).offset(skip).limit(limit).all()

    return {
        "message": "Notification retrieved successfully",
        "status": "ok",
        "data": notifications
    }

# Patch request to update read_receipt
@router.patch('/notification/all', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    notifications = db.query(Notifications).filter(Notifications.profile_id == profile_model.id, Notifications.is_read == False).all()

    for notification in notifications:
        notification.is_read = True
    db.commit()
    return {
        "message": "all notifications marked as read",
        "status": "ok"
    }

@router.patch('/notification/{id}', status_code=status.HTTP_200_OK, response_model=NotificationResponse)
async def read_notification(id: str, db: db_dependency, user: user_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    notification_model = db.query(Notifications).filter(Notifications.profile_id == profile_model.id, Notifications.id == id).first()

    if not notification_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification_model.is_read = True
    db.commit()
    db.refresh(notification_model)
    
    return {
        "message": "notification marked as read",
        "status": "ok",
        "data": notification_model
    }

@router.post("/address", status_code=201)
async def add_address(request: AddressSchema, db: db_dependency, user: user_dependency, bgtask: BackgroundTasks):
    profile_model = get_profile_model(db, user.get('id'))
    address_model = db.query(Address).filter(Address.profile_id == profile_model.id).first()

    if address_model:
        raise HTTPException(status_code=400, detail="Address already exists")
    
    point = ST_GeomFromText(f'POINT({request.longitude} {request.latitude})', 4326)

    address_model = Address(
        id=str(uuid4()),
        profile_id=profile_model.id,
        address1=request.address1,
        address2=request.address2,
        city=request.city,
        state=request.state,
        country=request.country,
        geom=point
    )
    db.add(address_model)
    db.commit()
    db.refresh(address_model)

    # send notification 
    bgtask.add_task(NOTIFY.create, db, profile_model.id, "New Address added", NOTIFICATION.new_address, fullname=profile_model.user.fullname)

    return {
        "message": "address added successfully",
        "status": "ok", 
    }

@router.put("/address", status_code=status.HTTP_200_OK)
async def update_address(request: AddressSchema, db: db_dependency, user: user_dependency, bgtask: BackgroundTasks):
    profile_model = get_profile_model(db, user.get('id'))
    address_model = db.query(Address).filter(Address.profile_id == profile_model.id).first()

    if not address_model:
        raise HTTPException(status_code=404, detail="Address not found")
    
    point = ST_GeomFromText(f'POINT({request.longitude} {request.latitude})', 4326)

    address_model.address1 = request.address1
    address_model.address2 = request.address2
    address_model.city = request.city
    address_model.state = request.state
    address_model.country = request.country
    address_model.geom = point
    db.commit()
    db.refresh(address_model)

    # send notification 
    bgtask.add_task(NOTIFY.create, db, profile_model.id, "Address updated", NOTIFICATION.address_updated, fullname=profile_model.user.fullname)

    return {
        "message": "address updated successfully",
        "status": "ok", 
    }

@router.post("/profile-image", status_code=201)
async def upload_profile_image(image: UploadFile, db: db_dependency, user: user_dependency):
    profile_model = db.query(Profile).filter(Profile.user_id == user.get('id')).first()

    if not profile_model:
        raise HTTPException(status_code=404, detail="User not found")

    image_url = await upload_pic(image.file, profile_model.user.fullname)
    
    profile_model.profile_image = image_url
    db.commit()
    db.refresh(profile_model)

    return {
        "message": "profile image uploaded successfully",
        "data": profile_model.profile_image
    }

@router.get('/t&c')
async def get_terms_and_conditions(db: db_dependency, r: redis_dependency, user: user_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    role = profile_model.user_role
    terms = await r.get("terms"+role)

    if not terms:
        t_and_c = db.query(TermsAndConditions).filter(TermsAndConditions.category == role).order_by(TermsAndConditions.created.desc()).first()
        
        if not t_and_c:
            raise HTTPException(status_code=404, detail="Terms and conditions not found")

        data = {
            "terms": t_and_c.terms,
            "created": t_and_c.created
        }
        await r.setex("terms"+role, 24*3600, json.dumps(data))
        return {
            "message": "FAQs retrieved successfully",
            "status": "ok",
            "data": data
        }
    
    return {
        "message": "FAQs retrieved successfully",
        "status": "ok",
        "data": json.loads(terms)
    }

@router.get('/faqs', status_code=status.HTTP_200_OK, response_model=FaqResponse)
async def get_faqs(db: db_dependency, r: redis_dependency, user: user_dependency):
    profile_model = get_profile_model(db, user.get('id'))
    role = profile_model.user_role
    faqs = await r.get("faqs"+role)

    if not faqs:
        data = db.query(Faqs).filter(Faqs.category == role).all()
        await r.setex("faqs"+role, 24*3600, json.dumps(data))
        return {
            "message": "FAQs retrieved successfully",
            "status": "ok",
            "data": data
        }

    return {
        "message": "FAQs retrieved successfully",
        "status": "ok",
        "data": json.loads(faqs)
    }
