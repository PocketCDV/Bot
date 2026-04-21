from fastapi import APIRouter

from app.asgi.api.v1.auth.router import auth_router

v1_router: APIRouter = APIRouter(prefix="/v1")

v1_router.include_router(auth_router)
