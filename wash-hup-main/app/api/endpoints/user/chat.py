from fastapi import APIRouter, status, Query, HTTPException
from ...dependencies import db_dependency, user_dependency, get_profile_model
from app.models.client.wash import Wash, WashMessage



router = APIRouter(
    prefix="/chat",
    tags=["Wash Chat"]
)

@router.get("/messages", status_code=status.HTTP_200_OK)
async def get_chat_mssages(
    db: db_dependency,
    washer: user_dependency,
    wash_id: str = Query(..., pattern=r"^[a-z0-9-_]+$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=30)
):
    profile_model = get_profile_model(db, washer.get("id"))
    

    if profile_model.user_role == "owner":
        wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.client_id == profile_model.id).first()
    elif profile_model.user_role == "washer":
        wash_model = db.query(Wash).filter(Wash.id == wash_id, Wash.washer_id == profile_model.id).first()
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid permission")

    if not wash_model:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "wash not found")
    
    messages = db.query(WashMessage).filter(WashMessage.wash_id == wash_id).offset(skip).limit(limit).all()

    if not messages:
        return {
            "message": "no messages found",
            "status": "ok"
        }
    
    return {
        "message": "messages retrieved successfully",
        "status": "ok",
        "data": messages
    }