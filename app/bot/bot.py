from aiogram import Dispatcher
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n, ConstI18nMiddleware
from redis.asyncio import Redis

from app.assets.controllers.session import SessionController
from app.bot.routes.start import start_router
from app.bot.scenes.home import HomeScene
from app.bot.scenes.start import StartScene
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
        session_controller=SessionController(redis),
    )

    ConstI18nMiddleware(
        locale="en",
        i18n=i18n,
    ).setup(new_dispatcher)

    new_dispatcher.include_routers(
        start_router,
    )

    SceneRegistry(new_dispatcher).add(
        StartScene,
        HomeScene,
    )

    return new_dispatcher
