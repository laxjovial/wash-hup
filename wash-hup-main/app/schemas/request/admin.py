from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Literal, Optional, List
from enum import Enum
from datetime import datetime
from app.models.admin.profile import Category


class SignUpForm(BaseModel):
    fullname: str = Field(
        min_length=3, 
        max_length=50,
        pattern=r"^[a-zA-Z0-9\s\-]+$",
        description="The user's name, containing only letters, numbers, and spaces.",
        )
    email: EmailStr
    password: str = Field(min_length=8) 
    role: Literal['admin'] = Field(
        description='Value must be "admin"'
    )
    phone_number: PhoneNumber = Field(
        min_length=10,
        description="User's phone number, e.g., +2348012345678",
        )
    
    model_config={
        'json_schema_extra': {
            'example': {
                'fullname': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'role': 'admin',
                'phone_number': '+2348010001123'
            }
        }
    }

class PriceUpdateSchema(BaseModel):
    quick_min: Optional[float] = None
    quick_max: Optional[float] = None
    smart_min: Optional[float] = None
    smart_max: Optional[float] = None
    premium_min: Optional[float] = None
    premium_max: Optional[float] = None

class FAQCreateSchema(BaseModel):
    category: Category
    question: str
    answer: str

class FAQUpdateSchema(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class TermsCreateSchema(BaseModel):
    category: Category
    terms: str

class RewardCreateSchema(BaseModel):
    title: str
    rating_required: float
    expiry_date: datetime

class DiscountCreateSchema(BaseModel):
    user_id: str
    title: str
    description: str
    total: int

class EmailSendSchema(BaseModel):
    recipients: List[str]
    subject: str
    body: str

class BroadcastEmailSchema(BaseModel):
    subject: str
    body: str

class AdminNotificationSchema(BaseModel):
    title: str
    message: str
