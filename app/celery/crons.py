import asyncio
import sys
from ssl import create_default_context

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select

from app.assets.controllers.api import APIController
from app.celery.worker import worker, config
from app.database.database import Database
from app.database.models import User


async def __async_session_refresh() -> None:
    """
    Asynchronously refresh every user's session ID.
    """

    database = Database.from_dsn(config.database_dsn.get_secret_value())
    redis = Redis.from_url(config.redis_dsn.get_secret_value(), decode_responses=True)
    api_controller = APIController(config.api_url, ssl_context=create_default_context(cafile=where()))

    bot: Bot = Bot(token=config.telegram_bot_token.get_secret_value())

    async with database.session_maker() as database_session:
        user_telegram_ids = await database_session.stream_scalars(
            select(User.telegram_id)
        )

        async for telegram_id in user_telegram_ids:
            telegram_id: int = int(telegram_id)

            state: FSMContext = FSMContext(
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

            session_id: str = await state.get_value("session_id")

            if session_id is None:
                continue

            new_session_id: str = await api_controller.refresh_session_id(session_id)
            await state.update_data(session_id=new_session_id)

            await asyncio.sleep(0.1)


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
