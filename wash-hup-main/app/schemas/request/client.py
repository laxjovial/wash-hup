from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum

# Address Schema 
class AddressRequest(BaseModel):
    address1: str = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]+$",
        description="Primary address line containing letters, numbers, spaces, commas, periods, and hyphens",
        min_length=5,
        max_length=100
    )
    address2: str | None = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]*$",
        description="Secondary address line (optional) containing letters, numbers, spaces, commas, periods, and hyphens",
        min_length=5,
        max_length=100
    )
    city: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
        description="City name containing only letters and spaces",
        min_length=2,
        max_length=50
    )
    state: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
        description="State name containing only letters and spaces",
        min_length=2,
        max_length=50
    )
    country: str = Field(
        pattern=r"^[a-zA-Z\s]+$",
        description="Country name containing only letters and spaces",
        min_length=2,
        max_length=50
    )


class PaymentType(str, Enum):
    CARD = "card"
    TRANSFER = "transfer"
    WALLET = "wallet"

class PaymentMethodRequest(BaseModel):
    payment_method: PaymentType = Field(
        description="Payment method identifier (e.g., card token, bank account ID)",
    )

class ProfileUpdateRequest(BaseModel):
    password: str 
    fullname: str | None = Field(
        default=None,
        pattern=r"^[a-zA-Z\s]+$",
        min_length=5,
        max_length=50
    )
    email: EmailStr | None = None
    phone_number: PhoneNumber | None = None
    payment_method: PaymentType | None = None


# Wash Requests 
class WashType(str, Enum):
    QUICK = 'quick'
    SMART = 'smart'
    PREMIUM = 'premium' 

class CreateLocation(BaseModel):
    name: str = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]*$",
        min_length=2
    )
    latitude: float = Field(..., ge=-85, le=85)
    longitude: float = Field(..., gt=-180, le=180)

class CreateWashRequest(BaseModel):
    location: CreateLocation
    bucket_avl: bool
    water_avl: bool
    wash_type: WashType

class CarType(str, Enum):
    SEDAN = 'sedan'
    VAN = 'van'
    SUV = 'suv'
    TRUCK = 'truck'
    COUPE = 'coupe'
    CONVERTIBLE = 'convertible'

class CreateCar(BaseModel):
    car_name: str = Field(
        pattern=r"^[a-zA-Z0-9\s,.-]*$",
        min_length=3
    )
    car_type: CarType
    color: str = Field(
        pattern=r"^[a-zA-Z\s]+$"
    )

class CreateCarRequest(BaseModel):
    wash_id: str = Field(
        pattern=r"^[a-z0-9-_]+$"
    )
    car: CreateCar

class VerifyRequest(BaseModel):
    wash_id: str
    code: str

class ReviewRequest(BaseModel):
    wash_id: str = Field(
        pattern=r"^[a-z0-9-_]+$"
    )
    review: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9.,\s]+$"
    )
    rating: float = Field(
        gt=0,
        lt=6
    )