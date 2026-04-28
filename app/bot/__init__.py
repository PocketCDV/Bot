from ssl import create_default_context

from aiogram import Dispatcher, BaseMiddleware
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore
from certifi import where
from redis.asyncio import Redis

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.client import ClientController
from app.assets.controllers.database import DatabaseController
from app.assets.controllers.schedule import ScheduleController
from app.bot.managers.locale import LocaleManager
from app.bot.middlewares.database import DatabaseMiddleware
from app.bot.middlewares.message_id import MessageIdMiddleware
from app.bot.middlewares.session_id import SessionIDMiddleware
from app.bot.middlewares.user import UserMiddleware
from app.bot.routes.home import home_router
from app.bot.routes.start import start_router
from app.bot.scenes.home import HomeScene
from app.bot.scenes.language import LanguageScene
from app.bot.scenes.schedule import ScheduleScene
from app.bot.scenes.start import StartScene
from config import config


def _register_middlewares(
        dispatcher: Dispatcher,
        *middlewares: BaseMiddleware,
) -> None:
    for middleware in middlewares:
        dispatcher.update.outer_middleware.register(middleware)


def create_dispatcher() -> Dispatcher:
    """
    Create a Dispatcher instance for managing all requests.

    :return: Dispatcher instance.
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
    schedule: ScheduleController = ScheduleController(
        cdv,
        database,
    )

    dispatcher = Dispatcher(
        storage=RedisStorage(
            redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
        fsm_strategy=FSMStrategy.GLOBAL_USER,
        config=config,
        database=database,
        redis=redis,
        client=client,
        cdv=cdv,
        schedule=schedule,
    )

    _register_middlewares(
        dispatcher,
        DatabaseMiddleware(database),
        UserMiddleware(),
        SessionIDMiddleware(cdv),
        MessageIdMiddleware(),
    )

    I18nMiddleware(
        core=FluentCompileCore(
            path="locales/{locale}",
            default_locale="en",
        ),
        manager=LocaleManager(
            default_locale="en",
        ),
    ).setup(dispatcher)

    dispatcher.include_routers(
        start_router,
        home_router,
    )

    SceneRegistry(dispatcher).add(
        StartScene,
        HomeScene,
        ScheduleScene,
        LanguageScene,
    )

    return dispatcher
