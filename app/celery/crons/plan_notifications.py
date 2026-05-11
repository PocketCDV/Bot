import asyncio
import sys
from datetime import datetime, timedelta
from ssl import create_default_context
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram_i18n.cores import FluentCompileCore
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select, or_

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.client import ClientController
from app.assets.controllers.database import DatabaseController
from app.assets.controllers.schedule import ScheduleController
from app.assets.enums.notification_kind import NotificationKind
from app.assets.exceptions import BotError
from app.assets.models.database import User, UserSettings, Notification
from app.assets.models.records.class_record import ClassRecord
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.celery.worker import worker, config
from app.utils import get_state, now_local


async def __async_plan_notifications() -> None:
    """
    Asynchronously plan all types of notifications for all users with notifications enabled.
    Writes Notification rows to be picked up later by the dispatch cron.
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

    tz: ZoneInfo = ZoneInfo(config.timezone)
    current_time: datetime = now_local()

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
            session_id: str | None = await state.get_value("session_id")

            if session_id is None:
                continue

            try:
                daily_schedule: DailyScheduleRecord = await schedule.get_home_schedule(session_id)
            except BotError:
                continue

            if not daily_schedule.class_records:
                continue

            daily_scheduled_at: datetime | None = None

            if settings.daily_class_notifications_enabled:
                earliest_start: datetime = min(
                    _aware(record.start_time, tz) for record in daily_schedule.class_records
                )
                nine_am: datetime = earliest_start.replace(hour=9, minute=0, second=0, microsecond=0)
                daily_scheduled_at = min(nine_am, earliest_start - timedelta(hours=1))

                session.add(
                    Notification(
                        user_id=user.id,
                        telegram_id=user.telegram_id,
                        kind=NotificationKind.DAILY,
                        scheduled_at=daily_scheduled_at,
                        data=daily_schedule.to_json(),
                    )
                )

            if settings.upcoming_class_notifications_enabled:
                for class_record in daily_schedule.class_records:
                    class_record: ClassRecord

                    if class_record.is_cancelled:
                        continue

                    scheduled_at: datetime = _aware(class_record.start_time, tz) - timedelta(hours=1)

                    if scheduled_at <= current_time:
                        continue

                    if daily_scheduled_at is not None and scheduled_at == daily_scheduled_at:
                        continue

                    session.add(
                        Notification(
                            user_id=user.id,
                            telegram_id=user.telegram_id,
                            kind=NotificationKind.UPCOMING,
                            scheduled_at=scheduled_at,
                            data=class_record.to_json(),
                        )
                    )

        await session.commit()


def _aware(value: datetime, tz: ZoneInfo) -> datetime:
    """
    Attach the local timezone to a naive datetime; pass-through if already aware.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=tz)

    return value


@worker.task(name="plan_notifications")
def plan_notifications() -> None:
    """
    Celery task for planning daily and upcoming notifications for every user.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_plan_notifications())
    else:
        asyncio.run(__async_plan_notifications())
