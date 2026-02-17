from fastapi import APIRouter
from ..user import auth, user, issues, chat
from ..client import index as owner_route
from ..admin import index as admin_route
from ..washer import index as washer_route
from app.websocket.router import router as websocket_route
from app.services.paystack import router as paystack_route



router = APIRouter(
    prefix='/v1'
)

router.include_router(auth.router)
router.include_router(user.router)
router.include_router(issues.router)
router.include_router(chat.router)
router.include_router(owner_route.router)
router.include_router(washer_route.router)
router.include_router(admin_route.router)
router.include_router(websocket_route)
router.include_router(paystack_route)