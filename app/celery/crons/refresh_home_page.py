import asyncio
import sys
from ssl import create_default_context

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext
from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers.memory import MemoryManager
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select, or_

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.client import ClientController
from app.assets.controllers.database import DatabaseController
from app.assets.controllers.schedule import ScheduleController
from app.assets.exceptions import BotError
from app.assets.exceptions.invalid_session import InvalidSessionError
from app.assets.models.database import User, UserSettings
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.bot.middlewares.user_message import UserMessage
from app.celery.worker import worker, config
from app.utils import get_state


async def __async_refresh_home_page() -> None:
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

    async with database.session() as session:
        stream = await session.stream(
            select(User, UserSettings)
            .join(UserSettings, User.id == UserSettings.user_id)
            .where(
                or_(
                    UserSettings.upcoming_class_notifications_enabled,
                    UserSettings.daily_class_notifications_enabled,
                )
            )
            .execution_options(yield_per=100)
        )

        async for user, settings in stream:
            user: User
            settings: UserSettings

            await asyncio.sleep(0.5)

            state: FSMContext = get_state(redis, bot, user.telegram_id)
            if await state.get_state() != "home":
                continue

            session_id: str = await state.get_value("session_id")
            user_message: UserMessage = UserMessage(
                user.telegram_id,
                await state.get_value("message_id"),
                _bot=bot,
            )
            i18n: I18nContext = I18nContext(
                settings.locale if settings else None,
                core,
                MemoryManager(),
                {},
            )

            try:
                daily_schedule: DailyScheduleRecord = await schedule.get_home_schedule(session_id)
            except InvalidSessionError:
                await user_message.ask_to_log_in(i18n)
                continue
            except BotError:
                continue

            await user_message.refresh_home_page(user, daily_schedule, i18n)


@worker.task(name="refresh_home_page")
def refresh_home_page() -> None:
    """
    Celery task for refreshing every user's home page.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_refresh_home_page())
    else:
        asyncio.run(__async_refresh_home_page())
