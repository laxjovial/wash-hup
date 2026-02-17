from .base import ResponseSchema
from pydantic import BaseModel


class UpcomingOfferSchema(BaseModel):
    wash_id: str
    profile_pic: str | None = None
    address: str
    washer_name: str
    bucket_avl: bool

class UpcomingOfferResponse(ResponseSchema):
    data: list[UpcomingOfferSchema]


class WashInfoSchema(BaseModel):
    client_name: str
    location: str
    car_detail: str
    bucket_avl: bool
    water_avl: bool
    wash_type: str
    rating: float
    progress: str
    price: float
    profile_pic: str | None = None

class WashDetailSchema(BaseModel):
    arrived_time: str | None = None
    completed_time: str | None = None

class ReviewSchema(BaseModel):
    review: str | None = None
    rating: int | None = None

class WashDetailData(BaseModel):
    wash_info: WashInfoSchema
    wash_detail: WashDetailSchema
    review: ReviewSchema

class WashDetailResponse(ResponseSchema):
    data: WashDetailData

class OngoingWashSchema(BaseModel):
    id: str
    client_name: str
    location: str
    car_name: str
    client_pic: str | None = None
    price: float

    class Config:
        from_attributes = True


class OngoingWashResponse(ResponseSchema):
    data: list[OngoingWashSchema]

class CompletedWashSchema(BaseModel):
    id: str
    client_name: str
    location: str
    car_name: str
    client_pic: str | None = None
    price: float
    washer_rating: float
    bucket_avl: bool

    class Config:
        from_attributes = True


class CompletedWashResponse(ResponseSchema):
    data: list[CompletedWashSchema]