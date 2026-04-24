import asyncio
from typing import Annotated

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from aiohttp import ClientConnectionError, ClientConnectorCertificateError
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.asgi.dependencies import config_dependency, redis_dependency, api_controller_dependency, \
    database_session_dependency
from app.asgi.limiter import limiter
from app.assets.controllers.api import APIController
from app.celery.tasks import insert_user_to_database, set_successful_login_message, update_state
from config import Config

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
async def login(
        request: Request,
        login_model: LoginModel,
        config: Annotated[Config, Depends(config_dependency)],
        database_session: Annotated[AsyncSession, Depends(database_session_dependency)],
        redis: Annotated[Redis, Depends(redis_dependency)],
        api_controller: Annotated[APIController, Depends(api_controller_dependency)],
) -> None:
    try:
        telegram_init_data: WebAppInitData = safe_parse_webapp_init_data(
            token=config.telegram_bot_token.get_secret_value(),
            init_data=login_model.telegram_init_data,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    try:
        session_id: str = await api_controller.get_session_id(login_model.login, login_model.password)

        if session_id is None or (await api_controller.refresh_session_id(session_id)) is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
    except HTTPException:
        raise
    except ClientConnectorCertificateError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SSL error when connecting to WU server",
        )
    except ClientConnectionError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach WU server",
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out",
        )

    await asyncio.to_thread(
        insert_user_to_database.delay,
        telegram_id=telegram_init_data.user.id,
        first_name=telegram_init_data.user.first_name,
        locale=telegram_init_data.user.language_code,
    )

    await asyncio.to_thread(
        update_state.delay,
        telegram_id=telegram_init_data.user.id,
        data={"session_id": session_id},
    )

    await asyncio.to_thread(
        set_successful_login_message.delay,
        telegram_id=telegram_init_data.user.id,
        locale=telegram_init_data.user.language_code,
    )
