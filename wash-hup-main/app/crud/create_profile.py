from app.models.client.profile import OwnerProfile
from app.models.washer.profile import WasherProfile
from app.models.admin.profile import AdminProfile
from .notifications import NOTIFY, NOTIFICATION
from app.utils.email import send_welcome_email, send_verify_email, subscribe_email
from .create_issue import create_issue
import uuid


    
async def create_user_profile(db, user_id: str, role: str):

    if role == "owner":
        profile = OwnerProfile
    elif role == "washer":
        profile = WasherProfile
    else:
        profile = AdminProfile
        
    profile_model = profile(
        id=str(uuid.uuid4()),
        user_id=user_id,
    )
    db.add(profile_model)
    db.commit()
    db.refresh(profile_model)

    if role == "admin":
        return
    
    await send_welcome_email(role, profile_model.user.fullname, profile_model.user.email)

    await NOTIFY.create(
        db, 
        profile_model.id, 
        "welcome to wash-hup", 
        message=NOTIFICATION.signup_owner if role == "owner" else NOTIFICATION.signup_washer,
        fullname=profile_model.user.fullname
    )
    await NOTIFY.create(
        db, 
        profile_model.id, 
        "Verify you email.", 
        message=NOTIFICATION.verify_email if role == "owner" else NOTIFICATION.verify_email, 
        fullname=profile_model.user.fullname, 
        email=profile_model.user.email
    )
    await send_verify_email(profile_model.user.fullname, profile_model.user.email, profile_model.id, role)
    create_issue(db, profile_model.user.id)

    await subscribe_email(profile_model.user.email, profile_model.user.fullname.split(" ")[0], profile_model.user.fullname.split(" ")[1])





    