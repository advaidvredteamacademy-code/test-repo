from fastapi import APIRouter
from .endpoints import health, claims

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(claims.router, tags=["claims"])

