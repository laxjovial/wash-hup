from .base import ResponseSchema
from pydantic import BaseModel


class ProfileSchema(BaseModel):
    user_id: str
    fullname: str
    phone_number: str
    email: str
    payment_method: str | None
    profile_pic: str | None 

class ProfileResponse(ResponseSchema):
    data: ProfileSchema

