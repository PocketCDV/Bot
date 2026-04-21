from fastapi import APIRouter

from app.asgi.api.v1.router import v1_router

api_router: APIRouter = APIRouter(prefix="/api")

api_router.include_router(v1_router)
