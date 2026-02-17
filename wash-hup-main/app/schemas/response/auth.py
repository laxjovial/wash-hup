from pydantic import BaseModel
from .base import ResponseSchema

class SignUpSchema(BaseModel):
    fullname: str
    email: str
    role: str
    phone_number: str

    class Config:
        from_attributes = True

class SignUpResponse(ResponseSchema):
    """
    Response schema for user creation.
    """

    user_id: str
    data: SignUpSchema

    model_config = {
        'json_schema_extra': {
            'example': {
                'status': 'ok',
                'message': 'User created successfully',
                'user_id': '123e4567-e89b-12d3-a456-426614174000',
                'data': {
                    'fullname': 'John Doe',
                    'email': 'john.doe@example.com',
                    'role': 'user',
                    'phone_number': '1234567890',
                }
            }
        }
    }

class LoginResponse(ResponseSchema):

    access_token: str
    token_type: str = 'bearer'

    model_config = {
        'json_schema_extra': {
            'example': {
                'status': 'ok',
                'message': 'Login successful',
                'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'token_type': 'bearer'
            }
        }
    }