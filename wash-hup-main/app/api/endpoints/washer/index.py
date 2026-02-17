from fastapi import APIRouter
from .profile import router as profile_router
from .setup import router as setup_router
from .offer import router as offer_router
from .wallet import router as wallet_router
from .rating import router as rating_router


router = APIRouter(
    prefix='/washer',
)

router.include_router(profile_router)
router.include_router(setup_router)
router.include_router(offer_router)
router.include_router(wallet_router)
router.include_router(rating_router)