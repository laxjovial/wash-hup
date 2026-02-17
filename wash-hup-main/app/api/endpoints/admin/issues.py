from fastapi import APIRouter, status, HTTPException, Body
from ...dependencies import admin_dependency, db_dependency, get_profile_model
from app.models.auth.user import Issue, IssueMessage
from uuid import uuid4
from datetime import datetime


router = APIRouter(
    prefix="/issues",
    tags=["Admin: Issues Management"]
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_all_issues(db: db_dependency, admin: admin_dependency, skip: int = 0, limit: int = 100):
    issues = db.query(Issue).offset(skip).limit(limit).all()
    return {"status": "success", "data": issues}

@router.get("/{issue_id}", status_code=status.HTTP_200_OK)
async def get_issue_details(issue_id: str, db: db_dependency, admin: admin_dependency):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    messages = db.query(IssueMessage).filter(IssueMessage.issue_id == issue_id).all()
    return {"status": "success", "data": {"issue": issue, "messages": messages}}

@router.post("/{issue_id}/respond", status_code=status.HTTP_201_CREATED)
async def respond_to_issue(issue_id: str, db: db_dependency, admin: admin_dependency, body: str = Body(..., embed=True)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    profile = get_profile_model(db, admin.get("id"))

    message = IssueMessage(
        id="ism_"+str(uuid4()),
        issue_id=issue_id,
        profile_id=profile.id,
        body=body,
        created=datetime.now()
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"status": "success", "message": "Response sent", "data": message}
