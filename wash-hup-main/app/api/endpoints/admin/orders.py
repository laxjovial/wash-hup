from fastapi import APIRouter, status
from ...dependencies import admin_dependency, db_dependency, redis_dependency
from app.models.admin.prices import ServicePrice
from uuid import uuid4


router = APIRouter(
    prefix="/orders",
    tags=["Admin: Orders"]
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_orders():
    pass

@router.get("/recent", status_code=status.HTTP_200_OK, tags=["Admin: Dashboard"])
async def get_recent_orders():
    pass

@router.get('/filter', status_code=status.HTTP_200_OK)
async def get_filtered_orders():
    pass

@router.get("/prices", status_code=status.HTTP_200_OK)
async def get_prices(db: db_dependency):
    pass

@router.post("/recommend-price",  status_code=status.HTTP_201_CREATED)
async def add_price(db: db_dependency):
    price_model = ServicePrice(
        id="pr_"+str(uuid4()),
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
async def update_price():
    pass