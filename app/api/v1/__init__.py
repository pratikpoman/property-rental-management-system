from fastapi import APIRouter
from app.api.v1.endpoints import auth, properties, tenants, agreements, payments, maintenance, dashboard

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(properties.router)
api_router.include_router(tenants.router)
api_router.include_router(agreements.router)
api_router.include_router(payments.router)
api_router.include_router(maintenance.router)
api_router.include_router(dashboard.router)
