from pydantic import BaseModel, Field
from typing import Literal, Any

from pydantic import BaseModel, Field
from enum import Enum

class BodyMessage(BaseModel):
    message: str = Field(
        min_length=1, 
        max_length=250,
        pattern=r"^[a-zA-Z0-9\s?!.\-,]+$",
        description="The user's name, containing only letters, numbers, and spaces.",
        )

class WSBase(BaseModel):
    action: str = Field(..., description="chat | issue | wash | notify")
    message: str

class ChatMessage(WSBase):
    action: Literal["chat"]

class IssueMessage(WSBase):
    action: Literal["issue"]

class AdminIssueMessage(WSBase):
    action: Literal["admin_issue"]
    issue_id: str

class WashCommand(WSBase):
    action: Literal["wash"]
    machine_id: str



def validate(data: dict): 
    import json

    data = json.loads(data)
    if not data.get('action'):
        return None
    if data["action"] == 'chat':
        valid_data = ChatMessage.model_validate(data)
        if valid_data:
            return valid_data.model_dump()
        else: 
            None
    elif data["action"] == 'issue':
        valid_data = IssueMessage.model_validate(data)
        if valid_data:
            return valid_data.model_dump()
        else: 
            None
    elif data["action"] == 'admin_issue':
        valid_data = AdminIssueMessage.model_validate(data)
        if valid_data:
            return valid_data.model_dump()
        else: 
            None
    elif data["action"] == 'wash':
        valid_data = WashCommand.model_validate(data)
        if valid_data:
            return valid_data.model_dump()
        else: 
            None
    else:
        return None