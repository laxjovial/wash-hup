from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.models.auth.user import User
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends, HTTPException


load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='v1/auth/login/')


def authenticate_user(db, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user


def create_access_token(email: str, user_id: str, role: str, expires_delta: timedelta):
    encode = {
        'sub': email,
        'id': user_id,
        'role': role
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(token: str):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        role: str = payload.get('role')

        if email is None or user_id is None or role is None:
            raise HTTPException(status_code=401, detail='Invalid authentication credentials')
        
        return {
            'email': email,
            'id': user_id,
            'role': role,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        role: str = payload.get('role')

        if email is None or user_id is None or role is None:
            raise HTTPException(status_code=401, detail='Invalid authentication credentials')
        
        return {
            'email': email,
            'id': user_id,
            'role': role,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')


async def get_owner_user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    if user['role'] != 'owner':
        raise HTTPException(status_code=403, detail='Not enough permissions to access this resource')
    return user


async def get_washer_user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')
    
    if user['role'] != 'washer':
        raise HTTPException(status_code=403, detail='Not enough permissions to access this resource')
    return user


async def get_admin_user(user: Annotated[dict, Depends(get_current_user)]):
    if user is None:
        raise HTTPException(status_code=401, detail='Not authenticated')
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Not enough permissions to access this resource')
    return user
