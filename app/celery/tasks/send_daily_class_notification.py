import asyncio
import sys
from typing import Any, Dict

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions
from aiogram_i18n import I18nContext
from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers.memory import MemoryManager

from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.bot.keyboards.dismiss import get_dismiss_keyboard
from app.celery.worker import worker, config


async def __async_send_daily_class_notification(
        telegram_id: int,
        locale: str | None,
        data: Dict[str, Any],
) -> None:
    """
    Asynchronously send a daily notification listing today's classes.
    :param telegram_id: User's telegram ID.
    :param locale: User's locale.
    :param data: JSON-serialized DailyScheduleRecord.
    """

    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    core = FluentCompileCore(path="locales/{locale}")
    await core.startup()

    i18n: I18nContext = I18nContext(locale, core, MemoryManager(), {})
    daily_schedule: DailyScheduleRecord = DailyScheduleRecord.from_json(data)

    await bot.send_message(
        chat_id=telegram_id,
        text=i18n.get(
            "notification-daily",
            classes=await daily_schedule.to_string(bot, i18n),
        ),
        reply_markup=get_dismiss_keyboard(i18n),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@worker.task(
    name="send_daily_class_notification",
    max_retries=3,
    default_retry_delay=5,
    ignore_result=True,
    time_limit=30,
    soft_time_limit=25,
)
def send_daily_class_notification(
        telegram_id: int,
        locale: str | None,
        data: Dict[str, Any],
) -> None:
    """
    Celery task for sending a daily class notification.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_send_daily_class_notification(telegram_id, locale, data))
    else:
        asyncio.run(__async_send_daily_class_notification(telegram_id, locale, data))
