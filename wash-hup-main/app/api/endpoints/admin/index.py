from fastapi import APIRouter
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .orders import router as orders_router
from .wallet import router as wallet_router
from .accounts import router as accounts_router
from .issues import router as issues_router
from .emails import router as emails_router
from .rewards import router as rewards_router
from .site import router as site_router



router = APIRouter(
    prefix="/admin"
)

router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(orders_router)
router.include_router(wallet_router)
router.include_router(accounts_router)
router.include_router(issues_router)
router.include_router(emails_router)
router.include_router(rewards_router)
router.include_router(site_router)
