from fastapi import APIRouter

from app.api.v1 import admin, admin_auth, admin_panel, auth, notifications, railway, rides, trips, wallet


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(railway.router)
api_router.include_router(rides.router)
api_router.include_router(wallet.router)
api_router.include_router(notifications.router)
api_router.include_router(trips.router)
api_router.include_router(admin.router)
api_router.include_router(admin_auth.router)
api_router.include_router(admin_panel.router)
