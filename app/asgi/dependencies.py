from typing import AsyncIterator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.assets.controllers.cdv import CDVController
from config import Config


async def config_dependency(request: Request) -> Config:
    """
    Config dependency.
    """

    return request.app.state.config


async def database_session_dependency(request: Request) -> AsyncIterator[AsyncSession]:
    """
    Database session dependency.
    """

    async with request.app.state.database.session() as database_session:
        yield database_session


async def redis_dependency(request: Request) -> Redis:
    """
    Redis dependency.
    """

    return request.app.state.redis


async def client_dependency(request: Request) -> CDVController:
    """
    API Client dependency.
    """

    return request.app.state.client


async def cdv_dependency(request: Request) -> CDVController:
    """
    CDV Controller dependency.
    """

    return request.app.state.cdv
