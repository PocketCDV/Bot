from aiogram import Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from config import config


def create_dispatcher() -> Dispatcher:
    """
    Create a Dispatcher instance for managing all requests.

    :return: Dispatcher instance.
    """

    i18n = I18n(path="locales", default_locale="en", domain="messages")
    redis = Redis.from_url(config.redis_dsn.get_secret_value())

    new_dispatcher = Dispatcher(
        storage=RedisStorage(
            redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
        config=config,
        i18n=i18n,
        redis=redis,
    )

    return new_dispatcher
