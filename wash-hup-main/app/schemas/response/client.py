from .base import ResponseSchema
from pydantic import BaseModel
from datetime import datetime
from ..request.client import WashType


# Notification Schema and Response
class NotificationSchema(BaseModel):
    id: str
    title: str
    message: str
    is_read: bool
    created: datetime

    class Config:
        from_attributes = True

class NotificationResponse(ResponseSchema):
    data: list[NotificationSchema] | NotificationSchema

# Transaction Schema and Response 
class TransactionSchema(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    amount: float
    status: str
    created_at: str

    class Config:
        from_attributes = True

class TransactionResponse(ResponseSchema):
    data: list[TransactionSchema] | TransactionSchema

# Address Schema and Response 
class AddressSchema(BaseModel):
    id: str
    address1: str
    address2: str | None
    city: str
    state: str
    country: str

    class Config:
        from_attributes = True

class AddressResponse(ResponseSchema):
    data: AddressSchema

class PaymentMethodSchema(BaseModel):
    payment_method: str
    updated: datetime

    class Config:
        from_attributes = True

class PaymentMethodResponse(ResponseSchema):
    data: PaymentMethodSchema

class ProfileSchema(BaseModel):
    fullname: str
    email: str
    phone_number: str
    payment_method: str | None = None
    profile_pic: str | None = None
    is_restricted: bool
    is_flagged: bool

class ProfileResponse(ResponseSchema):
    data: ProfileSchema

class FaqSchema(BaseModel):
    id: int
    question: str
    answer: str
    created: datetime

    class Config:
        from_attributes = True

class FaqResponse(ResponseSchema):
    data: list[FaqSchema]

class IssueSchema(BaseModel):
    id: str
    created: datetime

    class Config:
        from_attributes = True

class IssueResponse(ResponseSchema):
    data: IssueSchema | list[IssueSchema]

class IssueMessageSchema(BaseModel):
    id: str
    profile_id: str
    body: str

    class Config:
        from_attributes = True

class MessageResponse(ResponseSchema):
    data: IssueMessageSchema | list[IssueMessageSchema]


class CreateWashSchema(BaseModel):
    wash_id: str
    client_id: str
    location: str
    bucket_avl: bool
    water_avl: bool
    wash_type: WashType

class CreateWashResponse(ResponseSchema):
    data: CreateWashSchema

class CarSchema(BaseModel):
    car_name: str
    car_type: str
    color: str

    class Config:
        from_attributes = True

class CarResponse(ResponseSchema):
    data: CarSchema 
    
class WasherSchema(BaseModel):
    id: str
    fullname: str
    rating: bool
    pic: str | None = None
    washes: int
    flagged: bool

class WasherResponse(ResponseSchema):
    data: list[WasherSchema]


