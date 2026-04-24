from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.billing.router import router as billing_router
from app.modules.webhooks.router import router as webhooks_router
from app.modules.license.router import router as license_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.admin.router import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(billing_router)
api_router.include_router(webhooks_router)
api_router.include_router(license_router)
api_router.include_router(dashboard_router)
api_router.include_router(admin_router)
