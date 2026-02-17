from datetime import datetime
from fastapi import APIRouter, status, Query, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import StreamingResponse
from ...dependencies import db_dependency, washer_dependency, get_profile_model, redis_dependency
from app.utils.upload_image import upload_pic
from app.models.client.wash import Wash, Review, Car
from app.models.client.profile import OwnerProfile
from app.schemas.response.washer import UpcomingOfferResponse, ResponseSchema, WashDetailResponse, OngoingWashResponse, CompletedWashResponse
from app.websocket.router import manager
from app.crud.notifications import NOTIFICATION, NOTIFY
import io
import qrcode
import json
import random
import string


router = APIRouter(
    prefix="/offer",
    tags=["Washer: Accept Offer"]
)

# todo
# 1. notification and emails 

@router.get("/upcoming-offers", status_code=status.HTTP_200_OK, response_model=UpcomingOfferResponse)
async def get_upcoming_offers(
    db: db_dependency, 
    washer: washer_dependency, 
    r: redis_dependency
):
    profile_model = get_profile_model(db, washer.get("id"))

    offer_key = f"offers:{profile_model.id}"
    offers = await r.hgetall(offer_key)

    if not offers:
        return {
            "message": "no offers found",
            "status": "ok",
            "data": []
        }
    
    offers = [json.loads(offer) for offer in offers.values()]
    data = [offer.get("payload") for offer in offers]
    
    return {
        "message": "offers retrieved successfully",
        "status": "ok",
        "data": data
    }

@router.post("/send-price-offer", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
async def send_price_offer(
    db: db_dependency,
    washer: washer_dependency,
    r: redis_dependency,
    bgtask: BackgroundTasks,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$"),
    price: float = Query(..., gt=0)
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    offer_key = f"offers:{profile_model.id}"
    offer = await r.hget(offer_key, wash_id)

    if not offer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "offer not found")
    
    offer = json.loads(offer)
    offer["payload"]["price"] = price
    
    await r.hset(offer_key, wash_id, json.dumps(offer))
    bgtask.add_task(NOTIFY.create, db, wash_model.client_id, "Wash Price Offer", NOTIFICATION.price_offer, fullname=profile_model.user.fullname, washer_name=profile_model.user.fullname)
    await manager.send_personal(offer, wash_model.client_id)

    return {
        "message": "offer sent successfully",
        "status": "ok",
    }

@router.post("/accept-offer", status_code=status.HTTP_200_OK, response_model=ResponseSchema)
async def accept_offer(
    db: db_dependency, 
    washer: washer_dependency, 
    r: redis_dependency, 
    bgtask: BackgroundTasks,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    offer_key = f"offers:{profile_model.id}"
    offer = await r.hget(offer_key, wash_id)

    if not offer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "offer not found")
    
    wash_model.washer_id = profile_model.id
    wash_model.washer_name = profile_model.user.fullname
    wash_model.pic = profile_model.profile_image

    offer = json.loads(offer)
    
    try: 
        offer.get("payload")["accepted"]
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "price not accepted by car owner.")
    
    wash_model.price = offer["payload"]["price"]
    wash_model.accepted = True
    
    db.commit()
    db.refresh(wash_model)

    await r.hdel(offer_key, wash_id)

    bgtask.add_task(NOTIFY.create, db, wash_model.client_id, "Wash accepted", NOTIFICATION.wash_accepted, fullname="Car owner", washer=profile_model.user.fullname)
    bgtask.add_task(NOTIFY.create, db, profile_model.id, "Offer accepted", NOTIFICATION.offer_accepted, fullname=profile_model.user.fullname)

    return {
        "message": "offer accepted successfully",
        "status": "ok",
    }

@router.get("/wash-detail", status_code=status.HTTP_200_OK, response_model=WashDetailResponse)
async def get_wash_details(
    db: db_dependency,
    washer: washer_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.washer_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    client_model = db.query(OwnerProfile).filter(OwnerProfile.id == wash_model.client_id).first()
    
    if not client_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "client not found")
    
    review_model = db.query(Review).filter(Review.wash_id == wash_model.id).first()
    car_model = db.query(Car).filter(Car.wash_id == wash_model.id).first()

    if not car_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "car not found")
    
    if wash_model.completed:
        progress = "completed"
    elif wash_model.started:
        progress = "ongoing"
    elif wash_model.washer_id:
        progress = "pending"
    else:
        progress = "upcoming"
    
    wash_info = {
        "client_name": client_model.user.fullname,
        "location": wash_model.location.location,
        "car_detail": car_model.car_name,
        "bucket_avl": wash_model.bucket_avl,
        "water_avl": wash_model.water_avl,
        "wash_type": wash_model.wash_type,
        "rating": profile_model.rating,
        "progress": progress,
        "price": wash_model.price,
        "profile_pic": profile_model.profile_image
    }
    wash_detail = {
        "arrived_time": wash_model.time_started if wash_model.started else None,
        "completed_time": wash_model.time_completed if wash_model.completed else None,
    }

    review = {
        "review": review_model.review if review_model else None,
        "rating": review_model.rating if review_model else None
    }
    data = {
        "wash_info": wash_info,
        "wash_detail": wash_detail,
        "review": review
    }

    return {
        "message": "wash details retrieved successfully",
        "status": "ok",
        "data": data
    }

@router.get("/generate-code", status_code=status.HTTP_200_OK)
async def qr_code(
    db: db_dependency,
    washer: washer_dependency,
    r: redis_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.washer_id == profile_model.id).first()

    if not washer_dependency:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    # generate random alphanumeric code
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)

    # Create an image using the Pillow image factory
    img = qr.make_image(fill_color=(21, 94, 141), back_color=(230, 242, 254))

    # Save image to an in-memory binary stream
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    await r.setex(profile_model.id+wash_model.id, 600, code)
    print(code)

    # Return the image stream as a StreamingResponse
    return StreamingResponse(img_byte_arr, media_type="image/png")

@router.post("/end-wash", status_code=status.HTTP_200_OK)
async def end_wash(
    image: UploadFile,
    db: db_dependency,
    washer: washer_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.washer_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    if not wash_model.started:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wash not started")
    
    if wash_model.completed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wash already completed")
    
    wash_model.completed = True
    wash_model.time_completed = datetime.now()

    image_url = await upload_pic(image.file, wash_model.id)
    wash_model.image = image_url

    db.commit()
    db.refresh(wash_model)

    return {
        "message": "wash ended successfully",
        "status": "ok",
        "data": wash_model
    }

@router.get("/ongoing-offer", status_code=status.HTTP_200_OK, response_model=OngoingWashResponse)
async def get_ongoing_offer(
    db: db_dependency,
    washer: washer_dependency,
):
    profile_model = get_profile_model(db, washer.get("id"))

    active_washes = db.query(Wash).filter(Wash.washer_id == profile_model.id, Wash.accepted == True, Wash.completed == False).order_by(Wash.created.desc()).all()

    if not active_washes:
        return {
            "message": "no active offers found",
            "status": "ok",
            "data": []
        }
    
    return {
        "message": "ongoing offers retrieved successfully",
        "status": "ok",
        "data": active_washes
    }

@router.get("/completed-offer", status_code=status.HTTP_200_OK, response_model=CompletedWashResponse)
async def get_completed_offer(
    db: db_dependency,
    washer: washer_dependency,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=10, le=50)
):
    profile_model = get_profile_model(db, washer.get("id"))

    completed_washes = db.query(Wash).filter(Wash.washer_id == profile_model.id, Wash.completed == True).order_by(Wash.created.desc()).offset(skip).limit(limit).all()

    if not completed_washes:
        return {
            "message": "no completed offers found",
            "status": "ok",
            "data": []
        }
    
    return {
        "message": "completed offers retrieved successfully",
        "status": "ok",
        "data": completed_washes
    }

# todo
@router.post("/request-rating", status_code=status.HTTP_200_OK)
async def request_rating(
    db: db_dependency,
    washer: washer_dependency,
    bgtask: BackgroundTasks,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$"),
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.washer_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    bgtask.add_task(NOTIFY.create, db, wash_model.client_id, "Request a review", NOTIFICATION.request_review, fullname=profile_model.user.fullname)
    await manager.send_personal({
        "action": "review",
        "type": "request", 
        "payload": {
            "wash_id": wash_model.id,
            "profile_pic": profile_model.profile_image,
            "address": wash_model.location.location,
            "washer_name": profile_model.user.fullname
        }
    }, wash_model.client_id)

    return {
        "message": "request sent successfully",
        "status": "ok",
    }
