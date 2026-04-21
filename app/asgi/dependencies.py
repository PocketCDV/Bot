from starlette.requests import Request

from app.asgi.controllers.session import SessionController
from config import Config


async def config_dependency(request: Request) -> Config:
    return request.app.state.config


async def session_controller_dependency(request: Request) -> SessionController:
    return request.app.state.session_controller
