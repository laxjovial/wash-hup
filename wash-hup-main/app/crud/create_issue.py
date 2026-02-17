from app.api.dependencies import db_dependency, get_profile_model
from fastapi import HTTPException, status
from app.models.auth.user import Issue
from uuid import uuid4

class issues:
    def __init__(self, db: db_dependency, user_id: str):
        self.db = db
        self.profile_model = get_profile_model(db, user_id)
        self.issue_model = db.query(Issue).filter(Issue.profile_id == self.profile_model.id).first()

    def create(self):
        if self.issue_model:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="issue already exists")
        
        issue_model = Issue(
            id='issues_'+str(uuid4()),
            profile_id=self.profile_model.id
        )

        self.db.add(issue_model)
        self.db.commit()
        self.db.refresh(issue_model)

    def get(self):
        return self.issue_model

    def delete(self):
        self.db.delete(self.issue_model)
        self.db.commit()



def create_issue(db: db_dependency, user_id: str):
    profile_model = get_profile_model(db, user_id)

    issue_model = db.query(Issue).filter(Issue.profile_id == profile_model.id).first()

    if issue_model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="issue already exists")
    
    issue_model = Issue(
        id='issues_'+str(uuid4()),
        profile_id=profile_model.id
    )

    db.add(issue_model)
    db.commit()
    db.refresh(issue_model)

    return {
        "message": "issue created successfully",
        "status": "ok",
        "data": issue_model
    }