from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.assets.controllers.cdv import CDVController
from config import Config


async def config_dependency(request: Request) -> Config:
    return request.app.state.config


async def database_session_dependency(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.database.session_maker() as database_session:
        yield database_session


async def redis_dependency(request: Request) -> Redis:
    return request.app.state.redis


async def api_controller_dependency(request: Request) -> CDVController:
    return request.app.state.api_controller
