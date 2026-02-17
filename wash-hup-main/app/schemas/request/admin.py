from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Literal
from enum import Enum


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
        description='Value most be "owner" or "washer"'
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