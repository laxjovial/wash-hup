from fastapi import APIRouter, status
from ...dependencies import admin_dependency, db_dependency, redis_dependency
from app.models.admin.prices import ServicePrice
from uuid import uuid4


router = APIRouter(
    tags=["Admin: Dashboard"]
)

@router.get("/overview", status_code=status.HTTP_200_OK)
async def get_dashboard_overview():
    pass

@router.get("/trend-chart-data", status_code=status.HTTP_200_OK)
async def get_order_trend_chart_data():
    pass

@router.get("/disputes/recent", status_code=status.HTTP_200_OK)
async def get_recent_disputes():
    pass

@router.get("/activities/recent", status_code=status.HTTP_200_OK)
async def get_recent_washer_activities():
    pass

