from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis


def get_state(
        redis: Redis,
        bot: Bot,
        telegram_id: int,
) -> FSMContext:
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