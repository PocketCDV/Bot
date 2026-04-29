import asyncio
import sys
from datetime import datetime
from ssl import create_default_context
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers.memory import MemoryManager
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.client import ClientController
from app.assets.controllers.database import DatabaseController
from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.exceptions import BotError
from app.bot.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.home import get_home_keyboard
from app.bot.middlewares.user_message import UserMessage
from app.bot.utils import get_state
from app.celery.worker import worker, config
from app.database.models import User


async def __async_session_refresh() -> None:
    """
    Asynchronously refresh every user's session ID.
    """

    database: DatabaseController = DatabaseController.from_dsn(
        config.database_dsn.get_secret_value(),
    )
    redis: Redis = Redis.from_url(
        config.redis_dsn.get_secret_value(),
        decode_responses=True,
    )
    client: ClientController = ClientController(
        base_url="https://wu.cdv.pl",
    )
    cdv: CDVController = CDVController(
        client,
        ssl_context=create_default_context(cafile=where()),
    )
    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async with database.session() as database_session:
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

            new_session_id: str = await cdv.refresh_session_id(session_id)
            await state.update_data(session_id=new_session_id)


async def __async_home_page_refresh() -> None:
    """
    Asynchronously refresh data on every user's home page.
    """

    core = FluentCompileCore(path="locales/{locale}")
    await core.startup()

    database: DatabaseController = DatabaseController.from_dsn(
        config.database_dsn.get_secret_value(),
    )
    redis: Redis = Redis.from_url(
        config.redis_dsn.get_secret_value(),
        decode_responses=True,
    )
    client: ClientController = ClientController(
        base_url="https://wu.cdv.pl",
    )
    cdv: CDVController = CDVController(
        client,
        ssl_context=create_default_context(cafile=where()),
    )
    schedule: ScheduleController = ScheduleController(
        cdv,
        database,
    )
    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    async with database.session() as database_session:
        users = await database_session.stream_scalars(
            select(User)
        )

        async for user in users:
            await asyncio.sleep(0.1)

            user: User = user
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
            i18n: I18nContext = I18nContext(user.locale, core, MemoryManager(), {})

            try:
                schedule_day: ScheduleDayRecord = await schedule.get_home_schedule(session_id)
            except InvalidSessionError:
                await user_message.edit_login(i18n)
                continue
            except BotError:
                continue

            time: datetime = datetime.now(tz=ZoneInfo("Europe/Warsaw"))

            if schedule_day.class_records:
                await user_message.edit(
                    i18n.get(
                        "home-updated",
                        first_name=user.first_name,
                        classes=await schedule_day.to_string(bot, i18n),
                        updated=time.strftime("%H:%M"),
                    ),
                    reply_markup=get_home_keyboard(schedule_day, i18n),
                )
            else:
                await user_message.edit(
                    i18n.get(
                        "home-no-classes-updated",
                        first_name=user.first_name,
                        updated=time.strftime("%H:%M"),
                    ),
                    reply_markup=get_home_keyboard(schedule_day, i18n),
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
    """
    Celery task for refreshing every user's home page.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_home_page_refresh())
    else:
        asyncio.run(__async_home_page_refresh())
