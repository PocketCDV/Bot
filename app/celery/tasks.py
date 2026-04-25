import asyncio
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n.cores import FluentCompileCore
from redis.asyncio import Redis

from app.bot.actions.home import HomeAction
from app.bot.middlewares.message_id import UserMessage
from app.bot.utils import get_state
from app.celery.worker import worker, config


async def __async_set_successful_login_message(
        telegram_id: int,
        locale: str,
) -> None:
    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    core = FluentCompileCore(path="locales/{locale}")
    await core.startup()

    state: FSMContext = get_state(
        Redis.from_url(config.redis_dsn.get_secret_value()),
        bot,
        telegram_id,
    )

    user_message: UserMessage = UserMessage(
        telegram_id,
        await state.get_value("message_id"),
        _bot=bot,
    )

    await user_message.edit_message(
        core.get_translator(locale).format("login-success")[0],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=core.get_translator(locale).format("button-go-home")[0],
                        callback_data=HomeAction().pack(),
                    )
                ]
            ]
        )
    )


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
