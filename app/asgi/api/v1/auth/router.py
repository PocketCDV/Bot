import asyncio
from typing import Annotated

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from aiohttp import ClientConnectionError
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.asgi.api.v1.exceptions.invalid_credentials import InvalidCredentialsError
from app.asgi.api.v1.exceptions.invalid_telegram_init_data import InvalidTelegramInitDataError
from app.asgi.api.v1.exceptions.server_unavailable import ServerUnavailableError
from app.asgi.dependencies import (
    config_dependency,
    redis_dependency,
    database_session_dependency,
    cdv_dependency, bot_dependency
)
from app.asgi.limiter import limiter
from app.asgi.logger import logger
from app.assets.controllers.cdv import CDVController
from app.bot.utils import get_state
from app.celery.tasks import set_successful_login_message
from app.database.models import User
from config import Config

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT,
    name="Login via WU Credentials.",
)
@limiter.limit("5/minute")
async def login(
        request: Request,
        login_model: LoginModel,
        config: Annotated[Config, Depends(config_dependency)],
        database_session: Annotated[AsyncSession, Depends(database_session_dependency)],
        redis: Annotated[Redis, Depends(redis_dependency)],
        cdv: Annotated[CDVController, Depends(cdv_dependency)],
        bot: Annotated[Bot, Depends(bot_dependency)],
) -> None:
    """
    Login via WU login and password.

    Validates Telegram Init Data, retrieves user's session ID using WU Credentials.

    After successful retrieval - inserts new user in database if not present, updates session ID in bot cache,
    and creates a celery task which modifies user's message to inform about successful login.

    :param request: Request object (Used by rate limiter).
    :param login_model: WU Credentials model.
    :param config: Config dependency.
    :param database_session: Database session dependency.
    :param redis: Redis dependency.
    :param cdv: CDV Controller dependency.
    :param bot: Bot dependency.

    :raises InvalidCredentialsError: If invalid WU Credentials are provided.
    :raises InvalidTelegramInitDataError: If invalid Telegram Init Data is provided.
    :raises ServerUnavailableError: If WU Server is unavailable.
    """

    try:
        telegram_init_data: WebAppInitData = safe_parse_webapp_init_data(
            token=config.telegram_bot_token.get_secret_value(),
            init_data=login_model.telegram_init_data,
        )
    except ValueError:
        raise InvalidTelegramInitDataError("Invalid Telegram init data")

    try:
        session_id: str = await cdv.get_session_id(login_model.login, login_model.password)

        if session_id is None or (await cdv.refresh_session_id(session_id)) is None:
            raise InvalidCredentialsError("Invalid credentials")

        logger.info(
            f"User {telegram_init_data.user.id} logged in successfully."
        )
    except (ClientConnectionError, asyncio.TimeoutError):
        raise ServerUnavailableError("WU Server is unavailable")

    upsert = (
        insert(User)
        .values(
            telegram_id=telegram_init_data.user.id,
            first_name=telegram_init_data.user.first_name,
            locale=telegram_init_data.user.language_code,
        )
        .on_conflict_do_update(
            index_elements=["telegram_id"],
            set_={
                "first_name": telegram_init_data.user.first_name,
                "locale": telegram_init_data.user.language_code,
            },
        )
        .returning(User.telegram_id, User.locale)
    )
    telegram_id, locale = (await database_session.execute(upsert)).one()
    await database_session.commit()

    state: FSMContext = get_state(redis, bot, telegram_id)
    await state.update_data(session_id=session_id)

    set_successful_login_message.delay(
        telegram_id=telegram_id,
        locale=locale,
    )
