from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Path, status, BackgroundTasks
from ...dependencies import db_dependency, client_dependency, get_profile_model, redis_dependency
from app.models.client.wash import Wash, Location, Review, Car
from app.models.client.payment import Payment
from app.models.admin.prices import ServicePrice
from app.models.washer.profile import WasherProfile, Wallet
from app.utils.wash import getWasherFromList
from app.schemas.request.client import CreateWashRequest, CreateCarRequest, VerifyRequest, ReviewRequest
from app.schemas.response.client import CreateWashResponse, CarResponse, WasherResponse, ResponseSchema
from app.services.paystack import initialize_payment
from geoalchemy2.functions import ST_GeomFromText, ST_AsText
from app.crud.notifications import NOTIFICATION, NOTIFY
from uuid import uuid4
from app.websocket.router import manager
import json


router = APIRouter(
    prefix="/wash",
    tags=["Car owners: booking"]
)


@router.post("/book-wash", status_code=status.HTTP_201_CREATED, response_model=CreateWashResponse)
async def book_a_wash(
    wash_form: CreateWashRequest,
    db: db_dependency,
    user: client_dependency,
    bgtask: BackgroundTasks
):
    profile_model = get_profile_model(db, user.get("id"))

    point = ST_GeomFromText(
        f"POINT({wash_form.location.longitude} {wash_form.location.latitude})", 4326)
    location_model = Location(
        id="loc_"+str(uuid4()),
        location=wash_form.location.name,
        geom=point
    )
    db.add(location_model)
    db.commit()
    db.refresh(location_model)

    wash_model = Wash(
        id="wa_"+str(uuid4()),
        client_id=profile_model.id,
        location_id=location_model.id,
        bucket_avl=wash_form.bucket_avl,
        water_avl=wash_form.water_avl,
        wash_type=wash_form.wash_type.value,
        client_name=profile_model.user.fullname,
        client_pic=profile_model.profile_image
    )
    db.add(wash_model)
    db.commit()
    db.refresh(wash_model)

    bgtask.add_task(NOTIFY.create, db, profile_model.id, "Wash created", NOTIFICATION.wash_created, fullname=profile_model.user.fullname)
    
    data = {
        "wash_id": wash_model.id,
        "client_id": wash_model.client_id,
        "location": location_model.location,
        "bucket_avl": wash_model.bucket_avl,
        "water_avl": wash_model.water_avl,
        "wash_type": wash_model.wash_type
    }

    return {
        "message": "wash created successfully",
        "status": "ok",
        "data": data
    }


@router.post("/book-wash/car", status_code=status.HTTP_201_CREATED, response_model=CarResponse)
async def car_details(
    car_form: CreateCarRequest,
    db: db_dependency,
    user: client_dependency
):
    profile_model = get_profile_model(db, user.get("id"))
    wash_model = db.query(Wash).filter(
        Wash.id == car_form.wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="wash not found")

    if wash_model.cars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="car details already added for this wash")

    car_model = Car(
        id="ca_"+str(uuid4()),
        wash_id=wash_model.id,
        car_type=car_form.car.car_type,
        car_name=car_form.car.car_name,
        color=car_form.car.color
    )
    db.add(car_model)
    db.commit()
    db.refresh(car_model)

    wash_model.car_name = car_model.car_name
    db.commit()

    wash_car = db.query(Car).filter(Car.wash_id == wash_model.id).first()

    return {
        "message": "car details added successfully",
        "status": "ok",
        "data": wash_car
    }


@router.get("/washers", status_code=status.HTTP_200_OK, response_model=WasherResponse)
async def get_cars_washers_close_by(
    r: redis_dependency,
    db: db_dependency,
    user: client_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, user.get("id"))
    wash_model = db.query(Wash).filter(
        Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="wash not found")

    wash_location = db.query(ST_AsText(Location.geom)).filter(
        Location.id == wash_model.location_id).scalar()
    longitude = float(wash_location.split("(")[1].split(" ")[0])
    latitude = float(wash_location.split(" ")[1].split(")")[0])

    washers = await r.geosearch(
        "washers:location",
        longitude=longitude,
        latitude=latitude,
        radius=5,
        unit="km"
    )

    if not washers:
        return {
            "message": "no washers found nearby. Try again",
            "status": "ok",
            "data": []
        }
    data = getWasherFromList(washers, db)

    return {
        "message": "washers retrieved successfully",
        "status": "ok",
        "data": data
    }

@router.post("/send-offer/{washer_id}", status_code=status.HTTP_201_CREATED, response_model=ResponseSchema)
async def send_wash_offer(
    user: client_dependency,
    db: db_dependency,
    r: redis_dependency,
    bgtask: BackgroundTasks,
    washer_id: str = Path(..., pattern=r"^[a-z0-9-]+$"),
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$"),
):
    profile_model = get_profile_model(db, user.get("id"))
    wash_model = db.query(Wash).filter(
        Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="wash not found")

    washer_model = db.query(WasherProfile).filter(
        WasherProfile.id == washer_id).first()

    if not washer_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="washer not found")

    data = {
        "action": "wash",
        "type": "send-offer",
        "payload": {
            "wash_id": wash_model.id,
            "profile_pic": profile_model.profile_image,
            "address": wash_model.location.location,
            "washer_name": profile_model.user.fullname,
            "bucket_avl": wash_model.bucket_avl
        }
    }

    offer_key = f"offers:{washer_model.id}"
    await r.hset(offer_key, wash_model.id, json.dumps(data))
    await r.expire(offer_key, 3600)  # Expire the hash after 1 hour

    bgtask.add_task(NOTIFY.create, db, washer_model.id, "Incoming Offer", NOTIFICATION.upcoming_offer, fullname=washer_model.user.fullname, client_name=profile_model.user.fullname)
    await manager.send_personal(data, washer_model.id)

    return {
        "message": "offer sent successfully",
        "status": "ok"
    }

@router.post("/accept-price-offer", status_code=status.HTTP_200_OK)
async def accept_price_offer(
    db: db_dependency,
    washer: client_dependency,
    redis: redis_dependency,
    bgtask: BackgroundTasks,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$"),
    washer_id: str = Query(..., pattern=r"^[a-z0-9-]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    
    offer_key = f"offers:{washer_id}"
    offer = await redis.hget(offer_key, wash_id)

    if not offer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "offer not found")
    
    data = json.loads(offer)
    

    try:
        data.get("payload")["price"]
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "price not found")
    
    data["payload"]["accepted"] = True
    
    await redis.hset(offer_key, wash_id, json.dumps(data))

    bgtask.add_task(NOTIFY.create, db, wash_model.washer_id, "Offer accepted", NOTIFICATION.price_offer_accepted, fullname="Washer", client_name=profile_model.user.fullname)
    await manager.send_personal(data, wash_model.washer_id)

    return {
        "message": "offer accepted successfully",
        "status": "ok"
    }

@router.get("/wash-detail", status_code=status.HTTP_200_OK)
async def get_wash_details(
    db: db_dependency,
    washer: client_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$")
):
    profile_model = get_profile_model(db, washer.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    washer_model = db.query(WasherProfile).filter(WasherProfile.id == wash_model.washer_id).first()
    
    if not washer_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "washer not found")
    
    car_model = db.query(Car).filter(Car.wash_id == wash_model.id).first()

    if not car_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "car not found")
    
    review_model = db.query(Review).filter(Review.wash_id == wash_model.id).first()
    
    if wash_model.completed:
        progress = "completed"
    elif wash_model.started:
        progress = "ongoing"
    elif wash_model.washer_id:
        progress = "pending"
    else:
        progress = "upcoming"
    
    wash_info = {
        "client_name": profile_model.user.fullname,
        "location": wash_model.location.location,
        "car_detail": car_model.car_name,
        "bucket_avl": wash_model.bucket_avl,
        "water_avl": wash_model.water_avl,
        "wash_type": wash_model.wash_type,
        "rating": washer_model.rating,
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

@router.post("/verify-wash", status_code=status.HTTP_200_OK)
async def verify_car_washer(VerifyRequest: VerifyRequest, db: db_dependency, r: redis_dependency, user: client_dependency):
    profile_model = get_profile_model(db, user.get("id"))
    wash_id = VerifyRequest.wash_id

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    if wash_model.is_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wash already verified")


    washer_model = db.query(WasherProfile).filter(WasherProfile.id == wash_model.washer_id).first()

    if not washer_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "washer not found")

    code = await r.getex(wash_model.washer_id+wash_model.id)
    print(code)

    if not code or code != VerifyRequest.code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid code")

    wash_model.washer_id = washer_model.id
    wash_model.is_verified = True
    wash_model.started = True
    wash_model.time_started = datetime.now(timezone.utc)

    db.commit()
    db.refresh(wash_model)

    return {
        "message": "Wash verified successfully",
        "status": "ok"
    }

@router.get("/pay/{wash_id}", status_code=status.HTTP_200_OK)
async def pay_washer(wash_id: str, db: db_dependency, user: client_dependency):
    profile_model = get_profile_model(db, user.get("id"))

    wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.client_id == profile_model.id).first()

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    if not wash_model.completed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wash not completed")
    
    wallet_model = db.query(Wallet).filter(Wallet.washer_id == wash_model.washer_id).first()

    payment = await initialize_payment(wash_model.price, profile_model.user.email, subaccount=wallet_model.id)

    if not payment["status"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, payment["message"])
    
    payment_model = Payment(
        id="pa_"+str(uuid4()),
        sender_id=profile_model.id,
        sender_name=profile_model.user.fullname,
        receiver_id=wash_model.washer_id,
        receiver_name=wash_model.washer_name,
        wash_id=wash_model.id,
        reference=payment["data"]["reference"],
        amount=wash_model.price,
        status="pending"
    )
    db.add(payment_model)
    db.commit()

    return {
        "message": "payment link created successfully",
        "status": "ok",
        "data": {
            "payment_link": payment["data"]["authorization_url"]
        }
    }

@router.post("/review")
async def rate_and_review_washer(review: ReviewRequest, db: db_dependency, user: client_dependency):
    profile_model = get_profile_model(db, user.get("id"))
    wash_model = db.query(Wash).filter(Wash.client_id == review.wash_id).first()

    if not wash_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="washer not found")

    review_model = Review(
        id="rt_"+str(uuid4()),
        wash_id=wash_model.id,
        client_id=profile_model.id,
        rating=review.rating,
        review=review.review
    )

    db.add(review_model)
    db.commit()
    db.refresh(review_model)

    return {
        "message": "review added successfully",
        "status": "ok",
        "data": review_model
    }

@router.get("/ongoing-washes", status_code=status.HTTP_200_OK)
async def get_ongoing_washes(db: db_dependency, user: client_dependency):
    profile_model = get_profile_model(db, user.get("id"))
    washes = db.query(Wash).filter(Wash.client_id == profile_model.id, Wash.started == True, Wash.completed == False).all()

    return {
        "message": "washes retrieved successfully",
        "status": "ok",
        "data": washes
    }

@router.get("/completed-washes")
async def get_all_washes(db: db_dependency, user: client_dependency, skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=10, le=50)):
    profile_model = get_profile_model(db, user.get("id"))
    washes = db.query(Wash).filter(Wash.client_id == profile_model.id, Wash.completed == True).offset(skip).limit(limit).all()

    return {
        "message": "washes retrieved successfully",
        "status": "ok",
        "data": washes
    }


@router.get("/prices")
async def get_services_prices(db: db_dependency, r: redis_dependency, user: client_dependency):
    get_profile_model(db, user.get("id"))
    prices = await r.get("service_prices")

    if not prices:
        prices = db.query(ServicePrice).order_by(
            ServicePrice.created.desc()).first()

        if not prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="prices not found")

        data = {
            "quick_min": prices.quick_min,
            "quick_max": prices.quick_max,
            "smart_min": prices.smart_min,
            "smart_max": prices.smart_max,
            "premium_min": prices.premium_min,
            "premium_max": prices.premium_max
        }
        await r.setex("service_prices", 3600, json.dumps(data))

        return {
            "message": "prices retrieved successfully",
            "status": "ok",
            "data": data
        }

    return {
        "message": "prices retrieved successfully",
        "status": "ok",
        "data": json.loads(prices)
    }