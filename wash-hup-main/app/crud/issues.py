from app.models.auth.user import Issue, IssueMessage
from app.websocket.schema import BodyMessage
from uuid import uuid4



async def create_issue_message(db, profile, data: str) -> str:
    issue_model = db.query(Issue).filter(Issue.profile_id == profile.id).first()

    if not issue_model:
        return "issue_error"
    try:
        message = BodyMessage.model_validate({"message": data})
    except: 
        return "invalid_message"

    
    message_model = IssueMessage(
        id="i-"+str(uuid4()),
        issue_id=issue_model.id,
        profile_id=profile.id,
        body=message.message
    )

    db.add(message_model)
    db.commit()
    db.refresh(message_model)

    return {
        "message": "issue created",
        "data": message_model
    }


async def create_issue_message_admin(db, profile, data: dict):
    issue_model = db.query(Issue).filter(Issue.id == data.get('issue_id')).first()

    if not issue_model:
        return "issue_error"
    try:
        message = BodyMessage.model_validate({"message": data['message']})
    except: 
        return "invalid_message"
    
    message_model = IssueMessage(
        id="i-"+str(uuid4()),
        issue_id=issue_model.id,
        profile_id=profile.id,
        body=message.message
    )

    db.add(message_model)
    db.commit()
    db.refresh(message_model)

    return {
        "message": "issue created",
        "data": message_model,
        "owner_id": issue_model.profile_id
    }

