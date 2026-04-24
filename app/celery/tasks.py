import asyncio
import sys
from typing import Any, Dict

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n.cores import FluentRuntimeCore
from redis.asyncio import Redis
from sqlalchemy.dialects.postgresql import insert

from app.bot.actions.home import HomeAction
from app.bot.middlewares.message_id import UserMessage
from app.bot.utils import get_state
from app.celery.worker import worker, config
from app.database.database import Database
from app.database.models import User


async def __async_insert_user_to_database(
        telegram_id: int,
        first_name: str,
        locale: str,
) -> None:
    database: Database = Database.from_dsn(config.database_dsn.get_secret_value())

    async with database.session_maker() as database_session:
        await database_session.execute(
            insert(User).values(
                telegram_id=telegram_id,
                first_name=first_name,
                locale=locale,
            ).on_conflict_do_nothing(index_elements=["telegram_id"])
        )
        await database_session.commit()


async def __async_update_state(
        telegram_id: int,
        data: Dict[str, Any],
) -> None:
    state: FSMContext = get_state(
        Redis.from_url(config.redis_dsn.get_secret_value()),
        Bot(token=config.telegram_bot_token.get_secret_value()),
        telegram_id,
    )

    await state.update_data(data)


async def __async_set_successful_login_message(
        telegram_id: int,
        locale: str,
) -> None:
    bot: Bot = Bot(token=config.telegram_bot_token.get_secret_value())

    core = FluentRuntimeCore(path="locales/{locale}")
    await core.startup()

    state: FSMContext = get_state(
        Redis.from_url(config.redis_dsn.get_secret_value()),
        bot,
        telegram_id,
    )

    message_id: int = await state.get_value("message_id")
    user_message: UserMessage = UserMessage(
        telegram_id,
        message_id,
        _bot=bot,
    )

    await user_message.edit_message(
        core.get("login-success", locale=locale),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=core.get("button-go-home", locale=locale),
                        callback_data=HomeAction().pack(),
                    )
                ]
            ]
        )
    )


@worker.task(
    name="insert_user_to_database",
    max_retries=3,
    default_retry_delay=5,
    ignore_result=True,
    time_limit=30,
    soft_time_limit=25,
)
def insert_user_to_database(
        telegram_id: int,
        first_name: str,
        locale: str,
) -> None:
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_insert_user_to_database(telegram_id, first_name, locale))
    else:
        asyncio.run(__async_insert_user_to_database(telegram_id, first_name, locale))


@worker.task(
    name="update_state",
    max_retries=3,
    default_retry_delay=5,
    ignore_result=True,
    time_limit=30,
    soft_time_limit=25,
)
def update_state(
        telegram_id: int,
        data: Dict[str, Any],
) -> None:
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_update_state(telegram_id, data))
    else:
        asyncio.run(__async_update_state(telegram_id, data))


@worker.task(
    name="set_successful_login_message",
    max_retries=3,
    default_retry_delay=5,
    ignore_result=True,
    time_limit=30,
    soft_time_limit=25,
)
def set_successful_login_message(
        telegram_id: int,
        locale: str,
) -> None:
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_set_successful_login_message(telegram_id, locale))
    else:
        asyncio.run(__async_set_successful_login_message(telegram_id, locale))
