from fastapi import APIRouter
from .profile import router as profile_router
from .booking import router as booking_router
from ...dependencies import db_dependency, client_dependency, get_profile_model

router = APIRouter(
    prefix='/client',
)

router.include_router(profile_router)
router.include_router(booking_router)