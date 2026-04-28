import asyncio
from typing import Annotated

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from aiohttp import ClientConnectionError, ClientConnectorCertificateError
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.asgi.dependencies import (
    config_dependency,
    redis_dependency,
    database_session_dependency,
    cdv_dependency
)
from app.asgi.limiter import limiter
from app.assets.controllers.cdv import CDVController
from app.bot.utils import get_state
from app.celery.tasks import set_successful_login_message
from app.database.models import User
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
        cdv: Annotated[CDVController, Depends(cdv_dependency)],
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
        session_id: str = await cdv.get_session_id(login_model.login, login_model.password)

        if session_id is None or (await cdv.refresh_session_id(session_id)) is None:
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

    await database_session.execute(
        insert(User).values(
            telegram_id=telegram_init_data.user.id,
            first_name=telegram_init_data.user.first_name,
            locale=telegram_init_data.user.language_code,
        ).on_conflict_do_nothing(index_elements=["telegram_id"])
    )
    await database_session.commit()

    user: User | None = await database_session.scalar(
        select(User)
        .filter_by(telegram_id=telegram_init_data.user.id).limit(1)
    )

    state: FSMContext = get_state(
        redis,
        Bot(token=config.telegram_bot_token.get_secret_value()),
        user.telegram_id,
    )
    await state.update_data(session_id=session_id)

    await asyncio.to_thread(
        set_successful_login_message.delay,
        telegram_id=user.telegram_id,
        locale=user.locale,
    )
