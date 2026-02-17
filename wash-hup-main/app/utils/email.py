import os
from app.api.dependencies import redis_dependency
from app.core.security import create_access_token
from datetime import timedelta
from uuid import uuid4
from dotenv import load_dotenv
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


async def send_welcome_email(role: str, username: str, email: str):
    resend.Emails.send({
        "from": "Wash-Hup <onboarding@mail.washhup.com>",
        "to": [email],
        "template": {
            "id": "welcome-owner" if role == "owner" else "welcome-washer",
            "variables": {
                "username": username
            }
        }, 
        "scheduled_at": "in 15 min"
    })

async def send_verify_email(username: str, email: str, user_id: str, role: str):
    token = create_access_token(email, user_id, role, expires_delta=timedelta(minutes=30)) 
                                 
    resend.Emails.send({
        "from": "Wash-Hup <onboarding@mail.washhup.com>",
        "to": [email],
        "template": {
            "id": "verify-email",
            "variables": {
                "username": username,
                "token": token
            }
        }, 
    })

async def send_forget_password_email(email: str, token: str):
    resend.Emails.send({
        "from": "Wash-Hup Support <support@mail.washhup.com>",
        "to": [email],
        "template": {
            "id": "forget-password",
            "variables": {
                "token": token
            }
        }, 
    })

async def subscribe_email(email: str, first_name: str, last_name: str, unsubscribed: bool = False):
    resend.Contacts.CreateParams = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "unsubscribed": unsubscribed,
    }
    