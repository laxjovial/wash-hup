from fastapi import APIRouter, HTTPException, status
from app.models.admin.profile import Faqs
from ...dependencies import user_dependency, get_profile_model, db_dependency, redis_dependency
from app.models.auth.user import Issue, IssueMessage
from app.schemas.response.client import IssueResponse, MessageResponse
from uuid import uuid4


router = APIRouter(
    prefix='/issues',
    tags=["Issues"]
)



@router.get('/', status_code=status.HTTP_200_OK) #, response_model=IssueResponse) 
async def get_issues_messages(db: db_dependency, user: user_dependency, skip: int = 0, limit: int = 50):
    profile_model = get_profile_model(db, user.get('id'))
    issues = db.query(Issue).filter(Issue.profile_id == profile_model.id).first()
    
    if not issues:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="issues not found")
    
    issue_messages = db.query(IssueMessage).filter(IssueMessage.issue_id == issues.id).offset(skip).limit(limit).all()
    
    return {
        "message": "Issues retrieved successfully",
        "status": "ok",
        "data": issue_messages
    }
