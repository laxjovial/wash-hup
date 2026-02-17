from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from app.core.security import authenticate_user, create_access_token
from app.schemas.response.auth import SignUpResponse, LoginResponse
from app.core.security import bcrypt_context, get_user_from_token
from uuid import uuid4
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.create_profile import create_user_profile
from app.crud.notifications import NOTIFY, NOTIFICATION
from app.schemas.request.auth import EmailSchema, PasswordSchema
from app.schemas.request.admin import SignUpForm
from app.models.auth.user import User
from ...dependencies import db_dependency


router = APIRouter(
    tags=["Authentication"]
)


@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def create_admin(form_data: SignUpForm, db: db_dependency, bgTask: BackgroundTasks): 
    """
    Create a new admin account with a unique email and phone number.
    The phone number should be in the format '+234XXXXXXXXXX' where '234' is the country code for Nigeria.
    """
    # check if there's already an admin account
    admin = db.query(User).filter(User.role == 'admin').first()

    if admin:
        raise HTTPException(status_code=400, detail='admin account already exist')
    
    # validate if email or phone number already exist
    user_with_email = db.query(User).filter(User.email == form_data.email).first() 
    user_with_number = db.query(User).filter(User.phone_number == form_data.phone_number[4:]).first()

    if user_with_email or user_with_number:
        raise HTTPException(status_code=400, detail='user with email or phone number already exist')
    
    create_user_model = User(
        id=str(uuid4()),
        fullname=form_data.fullname,
        email=form_data.email,
        role=form_data.role,
        phone_number=form_data.phone_number[4:],
        hashed_password=bcrypt_context.hash(form_data.password),
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    # create user profile 
    bgTask.add_task(create_user_profile, db, create_user_model.id, create_user_model.role)
    # send email for email verification
    # background.add_task(
    #     send_email, 
    #     subject="Welcome to WashHup", 
    #     body=f"http://localhost:8000/auth/login?token={token}", 
    #     recipient=create_user_model.email)
    
    return {
        'status': "ok",
        'message': "User created successfully",
        'user_id': create_user_model.id,
        'data': {
            'email': create_user_model.email,
            'fullname': create_user_model.fullname,
            'role': create_user_model.role,
            'phone_number': create_user_model.phone_number,
            'password': create_user_model.hashed_password
        }
    }