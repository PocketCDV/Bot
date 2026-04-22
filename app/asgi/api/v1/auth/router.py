from typing import Annotated

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.asgi.dependencies import config_dependency, session_controller_dependency, message_controller_dependency
from app.asgi.limiter import limiter
from app.assets.controllers.message import MessageController
from app.assets.controllers.session import SessionController
from app.bot.actions.home import HomeAction
from config import Config, config

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
        session_controller: Annotated[SessionController, Depends(session_controller_dependency)],
        message_controller: Annotated[MessageController, Depends(message_controller_dependency)],
        background_tasks: BackgroundTasks,
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

    session_id: str = await session_controller.try_fetch_session(
        login_model.login,
        login_model.password,
    )

    background_tasks.add_task(
        session_controller.set_session,
        telegram_id=telegram_init_data.user.id,
        session_id=session_id,
        expire=None,
    )

    background_tasks.add_task(
        send_successful_login_message,
        telegram_id=telegram_init_data.user.id,
        message_controller=message_controller,
    )


# TODO: Replace with celery task
async def send_successful_login_message(
        telegram_id: int,
        message_controller: MessageController,
) -> None:
    message_id: int = await message_controller.get_message_id(telegram_id)

    await Bot(token=config.telegram_bot_token.get_secret_value()).edit_message_text(
        "Successful login",
        chat_id=telegram_id,
        message_id=message_id,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Go to Home Page", callback_data=HomeAction().pack())
                ]
            ]
        )
    )
