from .base import ResponseSchema
from pydantic import BaseModel


class ProfileSchema(BaseModel):
    user_id: str
    fullname: str
    profile_pic: str | None = None
    location: str | None = None

class ProfileResponse(ResponseSchema):
    data: ProfileSchema

