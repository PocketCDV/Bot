from datetime import date, datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import config


def get_state(
        redis: Redis,
        bot: Bot,
        telegram_id: int,
) -> FSMContext:
    """
    Returns user FSMContext instance.
    :param redis: Redis instance.
    :param bot: Bot instance.
    :param telegram_id: User's Telegram ID.
    :return:
    """

    return FSMContext(
        storage=RedisStorage(
            redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
        key=StorageKey(
            bot_id=bot.id,
            chat_id=telegram_id,
            user_id=telegram_id,
        )
    )


def now_local() -> datetime:
    """
    Returns the current time in the configured local timezone.
    """

    return datetime.now(ZoneInfo(config.timezone))


def today_local() -> date:
    """
    Returns today's date in the configured local timezone.
    """

    return now_local().date()
