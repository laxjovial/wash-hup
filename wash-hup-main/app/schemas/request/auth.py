from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum


class UserRole(str, Enum):
    OWNER = 'owner'
    WASHER = 'washer'

class SignUpForm(BaseModel):
    fullname: str = Field(
        min_length=3, 
        max_length=50,
        pattern=r"^[a-zA-Z0-9\s\-]+$",
        description="The user's name, containing only letters, numbers, and spaces.",
        )
    email: EmailStr
    password: str = Field(min_length=8) 
    role: UserRole = Field(
        description='Value most be "owner" or "washer"'
    )
    phone_number: PhoneNumber = Field(
        min_length=10,
        description="User's phone number, e.g., +2348012345678",
        )
    
    model_config={
        'json_schema_extra': {
            'example': {
                'fullname': 'John Doe',
                'email': 'john@example.com',
                'password': 'johndoe1',
                'role': 'owner',
                'phone_number': '+2348010001000'
            }
        }
    }

class EmailSchema(BaseModel):
    email: EmailStr

    model_config = {
        'json_schema_extra': {
            'example': {
                'email': 'john@example.com'
            }
        }
    }

class PasswordSchema(BaseModel):
    password: str = Field(min_length=8)

    model_config={
        'json_schema_extra': {
            'example': {
                'password': 'password'
            }
        }
    }

class AddressSchema(BaseModel):
    address1: str = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]+$",
    )
    address2: str = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]*$",
    )
    city: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
    )
    state: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
    )
    country: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
    )
    longitude: float = Field(
        ge=-180,
        le=180
    )
    latitude: float = Field(
        ge=-90,
        le=90
    )

    model_config = {
        'json_schema_extra': {
            'example': {
                'address1': '123 Main St, Springfield, USA',
                'address2': 'Apt 4B',
                'city': 'Springfield',
                'state': 'Massachusetts',
                'country': 'USA',
                'longitude': 40.7128,
                'latitude': 74.0060
            }
        }
    }