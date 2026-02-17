from fastapi import APIRouter, status, Body, Depends
from ...dependencies import admin_dependency, db_dependency
from app.models.auth.user import User
import os
import resend
from typing import List


router = APIRouter(
    prefix="/emails",
    tags=["Admin: Emails"]
)

@router.post("/send", status_code=status.HTTP_200_OK)
async def send_admin_email(
    admin: admin_dependency,
    recipients: List[str] = Body(...),
    subject: str = Body(...),
    body: str = Body(...)
):
    resend.api_key = os.getenv("RESEND_API_KEY")

    try:
        r = resend.Emails.send({
            "from": "Wash-Hup Admin <admin@mail.washhup.com>",
            "to": recipients,
            "subject": subject,
            "html": f"<p>{body}</p>"
        })
        return {"status": "success", "message": "Email sent successfully", "data": r}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/broadcast", status_code=status.HTTP_200_OK)
async def broadcast_email(
    db: db_dependency,
    admin: admin_dependency,
    subject: str = Body(...),
    body: str = Body(...)
):
    resend.api_key = os.getenv("RESEND_API_KEY")

    # Fetch all user emails
    users = db.query(User).all()
    emails = [user.email for user in users if user.email]

    if not emails:
        return {"status": "success", "message": "No recipients found"}

    # Resend supports batching or multiple recipients in 'to' (up to a limit)
    # For a large number of users, we might want to chunk this.
    try:
        # Simple implementation using a single call (works for up to 50 recipients in Resend free tier/standard)
        # For real broadcast, we should loop or use batching.
        chunk_size = 50
        for i in range(0, len(emails), chunk_size):
            chunk = emails[i:i + chunk_size]
            resend.Emails.send({
                "from": "Wash-Hup Broadcast <broadcast@mail.washhup.com>",
                "to": chunk,
                "subject": subject,
                "html": f"<p>{body}</p>"
            })

        return {"status": "success", "message": f"Broadcast sent to {len(emails)} users"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
