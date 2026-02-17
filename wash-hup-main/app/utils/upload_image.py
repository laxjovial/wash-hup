import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()


cloudinary.config( 
    cloud_name = os.getenv("CLOUD_NAME"), 
    api_key = os.getenv("API_KEY"), 
    api_secret = os.getenv("API_SECRET"),
    secure=True
)

async def upload_pic(file, name: str) -> str:
    upload_result = cloudinary.uploader.upload(file, public_id=name)
    return upload_result["secure_url"]