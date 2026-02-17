from pydantic import BaseModel


class ResponseSchema(BaseModel):
    """
    Base schema for all responses.
    """
    status: str
    message: str

