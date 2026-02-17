from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.create_profile import create_user_profile
from app.crud.notifications import NOTIFY, NOTIFICATION
from app.schemas.request.auth import SignUpForm, EmailSchema, PasswordSchema
from app.schemas.response.auth import SignUpResponse, LoginResponse
from app.models.auth.user import User
from app.utils.email import send_forget_password_email
from app.core.security import bcrypt_context, get_user_from_token, authenticate_user, create_access_token
from ...dependencies import db_dependency, limit_dependency, get_profile_model, redis_dependency
from typing import Annotated
import uuid
from datetime import timedelta



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/signup", status_code=201, response_model=SignUpResponse)
async def create_user(form_data: SignUpForm, db: db_dependency, bgTask: BackgroundTasks): 
    """
    Create a new user account with a unique email and phone number.
    The phone number should be in the format '+234XXXXXXXXXX' where '234' is the country code for Nigeria.

    Validate email and phone number for uniqueness
    send verification mail
    """
     
    # validate if email or phone number already exist
    user_with_email = db.query(User).filter(User.email == form_data.email).first() 
    user_with_number = db.query(User).filter(User.phone_number == form_data.phone_number[4:]).first()

    if user_with_email or user_with_number:
        raise HTTPException(status_code=400, detail='user with email or phone number already exist')
    
    create_user_model = User(
        id=str(uuid.uuid4()),
        fullname=form_data.fullname,
        email=form_data.email,
        role=form_data.role,
        phone_number=form_data.phone_number[4:],
        hashed_password=bcrypt_context.hash(form_data.password),
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    # create user profile and send email
    bgTask.add_task(create_user_profile, db, create_user_model.id, create_user_model.role)
    
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

@router.post("/login", status_code=200, response_model=LoginResponse) #, dependencies=[limit_dependency])
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency, bgTask: BackgroundTasks):
    """
    This endpoint allows user to log in by providing their email and password.\n
    The username field in the form is expected to be the user's email.
    """

    email = form_data.username
    user = authenticate_user(db, email, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    profile_model = get_profile_model(db, user.id)
    token = create_access_token(
        email=user.email,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=120)  # Token valid for 60 minutes
    )

    if user.role == 'owner':
        notification = NOTIFICATION.login_owner
    elif user.role == 'washer':
        notification = NOTIFICATION.login_washer
    else:
        notification = NOTIFICATION.login_admin

    bgTask.add_task(NOTIFY.create, db, profile_model.id, 'Successfully logged in.', notification, fullname=user.fullname)

    return {
        'status': 'ok',
        'message': 'Login successful',
        'access_token': token,
        'token_type': 'bearer'
    }

@router.post('/forget-password', status_code=200)
async def forget_password(email: EmailSchema, db: db_dependency, bgTask: BackgroundTasks):
    """
    Send a reset password email to the user's email address.
    """
    user_model = db.query(User).filter(User.email == email.email).first()

    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')
    
    token = create_access_token(
        email=user_model.email,
        user_id=user_model.id,
        role=user_model.role,
        expires_delta=timedelta(minutes=10)
    )

    bgTask.add_task(send_forget_password_email, user_model.email, token)

    return {'status': "ok", 'message': 'Password reset email sent'}

@router.patch('/verify-email', status_code=200)
async def verify_email(token: str, db: db_dependency, bgTask: BackgroundTasks):
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    user_model = db.query(User).filter(User.email == user['email']).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')
    
    user_model.is_email_verified = True
    profile_model = get_profile_model(db, user_model.id)
    db.commit()
    db.refresh(user_model)

    bgTask.add_task(NOTIFY.create, db, profile_model.id, 'Email verified.', NOTIFICATION.email_verfied, fullname=user_model.fullname)

    return {
        'status': 'ok',
        'message': 'Email verified successfully',
        'email': user_model.email,
    }
    
@router.patch('/reset-password', status_code=200)
async def reset_password(password: PasswordSchema, token: str, db: db_dependency, bgTask: BackgroundTasks):
    user = get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    user_model = db.query(User).filter(User.email == user['email']).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')
    
    user_model.hashed_password = bcrypt_context.hash(password.password)
    profile_model = get_profile_model(db, user_model.id)
    db.commit()
    db.refresh(user_model)

    bgTask.add_task(NOTIFY.create, db, profile_model.id, 'Password reset.', NOTIFICATION.password_change, fullname=user_model.fullname)

    return {
        'status': 'ok',
        'message': 'Email verified successfully',
        'email': user_model.email,
    }