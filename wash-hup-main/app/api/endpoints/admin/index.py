from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .orders import router as orders_router
from .wallet import router as wallet_router



router = APIRouter(
    prefix="/admin"
)

router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(orders_router)
router.include_router(wallet_router)