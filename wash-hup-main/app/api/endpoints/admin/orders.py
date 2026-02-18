from fastapi import APIRouter, status, HTTPException, Body
from ...dependencies import admin_dependency, db_dependency, get_profile_model
from app.models.admin.prices import ServicePrice
from app.models.client.wash import Wash, Review

from uuid import uuid4
from typing import Optional, List


router = APIRouter(
    prefix="/orders",
    tags=["Admin: Orders"]
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_orders(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    orders = db.query(Wash).offset(skip).limit(limit).all()
    return {"status": "success", "data": orders}

@router.get("/recent", status_code=status.HTTP_200_OK, tags=["Admin: Dashboard"])
async def get_recent_orders(db: db_dependency, admin: admin_dependency, limit: int = 10):
    orders = db.query(Wash).order_by(Wash.created.desc()).limit(limit).all()
    return {"status": "success", "data": orders}

@router.get('/filter', status_code=status.HTTP_200_OK)
async def get_filtered_orders(
    db: db_dependency,
    admin: admin_dependency,
    status_filter: Optional[str] = None,
    client_id: Optional[str] = None,
    washer_id: Optional[str] = None
):
    query = db.query(Wash)
    if status_filter == "completed":
        query = query.filter(Wash.completed == True)
    elif status_filter == "pending":
        query = query.filter(Wash.completed == False, Wash.accepted == False)
    elif status_filter == "in_progress":
        query = query.filter(Wash.started == True, Wash.completed == False)

    if client_id:
        query = query.filter(Wash.client_id == client_id)
    if washer_id:
        query = query.filter(Wash.washer_id == washer_id)

    orders = query.all()
    return {"status": "success", "data": orders}

@router.get("/prices", status_code=status.HTTP_200_OK)
async def get_prices(db: db_dependency, admin: admin_dependency):
    prices = db.query(ServicePrice).order_by(ServicePrice.created.desc()).first()
    if not prices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prices not set")
    return {"status": "success", "data": prices}

@router.post("/recommend-price",  status_code=status.HTTP_201_CREATED)
async def add_price(db: db_dependency, admin: admin_dependency):
    profile = get_profile_model(db, admin.get("id"))
    price_model = ServicePrice(
        id="pr_"+str(uuid4()),
        admin_id=profile.id,
        quick_min=2000,
        quick_max=4000,
        smart_min=4000,
        smart_max=6000,
        premium_min=6000,
        premium_max=10000
    )
    db.add(price_model)
    db.commit()
    db.refresh(price_model)
    return {
        "message": "price added successfully",
        "data": price_model
    }

@router.put("/prices/{price_id}", status_code=status.HTTP_200_OK)
async def update_price(
    price_id: str,
    db: db_dependency,
    admin: admin_dependency,
    quick_min: Optional[float] = Body(None),
    quick_max: Optional[float] = Body(None),
    smart_min: Optional[float] = Body(None),
    smart_max: Optional[float] = Body(None),
    premium_min: Optional[float] = Body(None),
    premium_max: Optional[float] = Body(None)
):
    price_model = db.query(ServicePrice).filter(ServicePrice.id == price_id).first()
    if not price_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price model not found")

    if quick_min is not None: price_model.quick_min = quick_min
    if quick_max is not None: price_model.quick_max = quick_max
    if smart_min is not None: price_model.smart_min = smart_min
    if smart_max is not None: price_model.smart_max = smart_max
    if premium_min is not None: price_model.premium_min = premium_min
    if premium_max is not None: price_model.premium_max = premium_max

    db.commit()
    db.refresh(price_model)
    return {"status": "success", "message": "Prices updated", "data": price_model}

@router.get("/reviews", status_code=status.HTTP_200_OK)
async def get_all_reviews(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    reviews = db.query(Review).offset(skip).limit(limit).all()
    return {"status": "success", "data": reviews}

@router.delete("/reviews/{review_id}", status_code=status.HTTP_200_OK)
async def delete_review(review_id: str, db: db_dependency, admin: admin_dependency):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"status": "success", "message": "Review deleted"}

