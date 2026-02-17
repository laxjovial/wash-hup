from app.models.washer.profile import WasherProfile
from app.models.admin.prices import ServicePrice
from fastapi import HTTPException


def getWasherFromList(washers: list[str], db: any):
    washers_list = []

    for washer in washers:
        washer_model = db.query(WasherProfile).filter(WasherProfile.id == washer).first()

        if not washer_model:
            continue

        data = {
            "id": washer_model.id,
            "fullname": washer_model.user.fullname,
            "rating": washer_model.rating,
            "pic": washer_model.profile_image,
            "washes": washer_model.total_washes,
            "flagged": washer_model.is_flagged
        }
        washers_list.append(data)
    
    return washers_list 
    