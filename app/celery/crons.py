import asyncio
import sys
from datetime import datetime
from ssl import create_default_context
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext
from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers.memory import MemoryManager
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.actions.switch_scene import SwitchSceneAction
from app.bot.middlewares.message_id import UserMessage
from app.bot.utils import get_state
from app.celery.worker import worker, config
from app.assets.controllers.database import Database
from app.database.models import User


async def __async_session_refresh() -> None:
    """
    Asynchronously refresh every user's session ID.
    """

    database = Database.from_dsn(config.database_dsn.get_secret_value())
    redis = Redis.from_url(config.redis_dsn.get_secret_value(), decode_responses=True)
    api_controller = CDVController(config.api_url, ssl_context=create_default_context(cafile=where()))

    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async with database.session_maker() as database_session:
        user_telegram_ids = await database_session.stream_scalars(
            select(User.telegram_id)
        )

        async for telegram_id in user_telegram_ids:
            await asyncio.sleep(0.1)

            telegram_id: int = int(telegram_id)
            state: FSMContext = get_state(redis, bot, telegram_id)

            session_id: str = await state.get_value("session_id")

            if session_id is None:
                continue

            new_session_id: str = await api_controller.refresh_session_id(session_id)
            await state.update_data(session_id=new_session_id)


async def __async_home_page_refresh() -> None:
    core = FluentCompileCore(path="locales/{locale}")
    await core.startup()

    database = Database.from_dsn(config.database_dsn.get_secret_value())
    redis = Redis.from_url(config.redis_dsn.get_secret_value(), decode_responses=True)
    schedule_controller: ScheduleController = ScheduleController(
        database,
        CDVController(config.api_url, ssl_context=create_default_context(cafile=where())),
    )

    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async with database.session_maker() as database_session:
        users = await database_session.stream_scalars(
            select(User)
        )

        async for user in users:
            user: User = user
            await asyncio.sleep(0.1)

            state: FSMContext = get_state(redis, bot, user.telegram_id)
            scene_state: str | None = await state.get_state()

            if scene_state is None or scene_state != "home":
                continue

            session_id: str = await state.get_value("session_id")
            user_message: UserMessage = UserMessage(
                user.telegram_id,
                await state.get_value("message_id"),
                _bot=bot,
            )

            schedule: ScheduleDayRecord = await schedule_controller.get_home_schedule(session_id)

            i18n: I18nContext = I18nContext(user.locale, core, MemoryManager(), {})

            reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=i18n.get("button-view-schedule"),
                            callback_data=SwitchSceneAction(scene="schedule").pack(),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=i18n.get("button-lang"),
                            callback_data=SwitchSceneAction(scene="language").pack(),
                        )
                    ],
                ]
            )

            time: datetime = datetime.now(tz=ZoneInfo("Europe/Warsaw"))

            if schedule.class_records:
                await user_message.edit_message(
                    i18n.get(
                        "home-updated",
                        first_name=user.first_name,
                        classes=schedule.to_string(i18n),
                        updated=time.strftime("%H:%M"),
                    ),
                    reply_markup=reply_markup,
                )
            else:
                await user_message.edit_message(
                    i18n.get(
                        "home-no-classes-updated",
                        first_name=user.first_name,
                        updated=time.strftime("%H:%M"),
                    ),
                    reply_markup=reply_markup,
                )


@worker.task(name="session_refresh")
def session_refresh() -> None:
    """
    Celery task for refreshing every user's session ID.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_session_refresh())
    else:
        asyncio.run(__async_session_refresh())


@worker.task(name="home_page_refresh")
def home_page_refresh() -> None:
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_home_page_refresh())
    else:
        asyncio.run(__async_home_page_refresh())
