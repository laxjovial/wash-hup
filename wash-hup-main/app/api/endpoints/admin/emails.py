from fastapi import APIRouter, status, Body, Depends
from ...dependencies import admin_dependency, db_dependency
from app.models.auth.user import User
from app.schemas.request.admin import EmailSendSchema, BroadcastEmailSchema
from app.schemas.response.admin import AdminBaseResponse
import os
import resend
from typing import List


router = APIRouter(
    prefix="/emails",
    tags=["Admin: Emails"]
)

@router.post("/send", status_code=status.HTTP_200_OK, response_model=AdminBaseResponse)
async def send_admin_email(
    admin: admin_dependency,
    data: EmailSendSchema
):
    resend.api_key = os.getenv("RESEND_API_KEY")

    sender = os.getenv("ADMIN_EMAIL_SENDER", "Wash-Hup Admin <admin@mail.washhup.com>")
    try:
        r = resend.Emails.send({
            "from": sender,
            "to": data.recipients,
            "subject": data.subject,
            "html": f"<p>{data.body}</p>"
        })
        return {"status": "success", "message": "Email sent successfully", "data": r}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/broadcast", status_code=status.HTTP_200_OK, response_model=AdminBaseResponse)
async def broadcast_email(
    db: db_dependency,
    admin: admin_dependency,
    data: BroadcastEmailSchema
):
    resend.api_key = os.getenv("RESEND_API_KEY")

    # Fetch all user emails
    users = db.query(User).all()
    emails = [user.email for user in users if user.email]

    if not emails:
        return {"status": "success", "message": "No recipients found"}

    # Resend supports batching or multiple recipients in 'to' (up to a limit)
    # For a large number of users, we might want to chunk this.
    sender = os.getenv("ADMIN_EMAIL_SENDER", "Wash-Hup Broadcast <broadcast@mail.washhup.com>")
    try:
        # Simple implementation using a single call (works for up to 50 recipients in Resend free tier/standard)
        # For real broadcast, we should loop or use batching.
        chunk_size = 50
        for i in range(0, len(emails), chunk_size):
            chunk = emails[i:i + chunk_size]
            resend.Emails.send({
                "from": sender,
                "to": chunk,
                "subject": data.subject,
                "html": f"<p>{data.body}</p>"
            })

        return {"status": "success", "message": f"Broadcast sent to {len(emails)} users"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
