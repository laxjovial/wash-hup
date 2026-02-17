from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum

class AccountDetailRequest(BaseModel):
    account_name: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    account_number: str = Field(
        min_length=10,
        max_length=10,
        pattern=r"^[0-9]+$"
    )
    bank_name: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    bank_code: str = Field(
        min_length=1,
        pattern=r"[0-9]+$"
    )

    # model_config={
    #     'json_schema_extra': {
    #         'example': {
    #             'fullname': 'John Doe',
    #             'email': 'john@example.com',
    #             'password': 'johndoe1',
    #             'role': 'owner',
    #             'phone_number': '+2348010001000'
    #         }
    #     }
    # }

class RewardRequestSchema(BaseModel):
    reward_id: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    address: str = Field(
        min_length=3,
        max_length=150,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    city: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    state: str = Field(
        min_length=3,
        pattern=r"^[a-zA-Z0-9\s]+$"
    )
    phone_number: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^[0-9]+$"
    )