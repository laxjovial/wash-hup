from fastapi import APIRouter, status
from ...dependencies import admin_dependency, db_dependency
from app.models.auth.user import User, Issue
from app.models.client.profile import OwnerProfile
from app.models.washer.profile import WasherProfile
from app.models.client.wash import Wash
from sqlalchemy import func
from datetime import datetime, timedelta


router = APIRouter(
    tags=["Admin: Dashboard"]
)

@router.get("/overview", status_code=status.HTTP_200_OK)
async def get_dashboard_overview(db: db_dependency, admin: admin_dependency):
    total_users = db.query(User).count()
    total_owners = db.query(OwnerProfile).count()
    total_washers = db.query(WasherProfile).count()
    total_washes = db.query(Wash).count()
    total_revenue = db.query(func.sum(Wash.price)).filter(Wash.completed == True).scalar() or 0.0
    active_washes = db.query(Wash).filter(Wash.started == True, Wash.completed == False).count()

    return {
        "status": "success",
        "data": {
            "total_users": total_users,
            "total_owners": total_owners,
            "total_washers": total_washers,
            "total_washes": total_washes,
            "total_revenue": total_revenue,
            "active_washes": active_washes
        }
    }

@router.get("/trend-chart-data", status_code=status.HTTP_200_OK)
async def get_order_trend_chart_data(db: db_dependency, admin: admin_dependency):
    # Get wash counts for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    trends = db.query(
        func.date(Wash.created).label('date'),
        func.count(Wash.id).label('count')
    ).filter(Wash.created >= start_date).group_by(func.date(Wash.created)).all()

    return {"status": "success", "data": trends}

@router.get("/disputes/recent", status_code=status.HTTP_200_OK)
async def get_recent_disputes(db: db_dependency, admin: admin_dependency, limit: int = 5):
    disputes = db.query(Issue).order_by(Issue.created.desc()).limit(limit).all()
    return {"status": "success", "data": disputes}

@router.get("/activities/recent", status_code=status.HTTP_200_OK)
async def get_recent_washer_activities(db: db_dependency, admin: admin_dependency, limit: int = 5):
    # Recent completed washes as activities
    activities = db.query(Wash).filter(Wash.completed == True).order_by(Wash.time_completed.desc()).limit(limit).all()
    return {"status": "success", "data": activities}
