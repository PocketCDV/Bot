import asyncio
import sys
from ssl import create_default_context

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from certifi import where
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncScalarResult

from app.assets.controllers.cdv import CDVController
from app.assets.controllers.client import ClientController
from app.assets.controllers.database import DatabaseController
from app.assets.models.database import User
from app.celery.worker import worker, config
from app.utils import get_state


async def __async_refresh_session() -> None:
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
        stream: AsyncScalarResult = await database_session.stream_scalars(
            select(User.telegram_id)
            .execution_options(yield_per=100)
        )

        async for telegram_id in stream:
            telegram_id: int

            await asyncio.sleep(0.5)

            state: FSMContext = get_state(redis, bot, telegram_id)
            session_id: str = await state.get_value("session_id")

            if session_id is None:
                continue

            new_session_id: str = await cdv.refresh_session_id(session_id)
            await state.update_data(session_id=new_session_id)


@worker.task(name="refresh_session")
def refresh_session() -> None:
    """
    Celery task for refreshing every user's session ID.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_refresh_session())
    else:
        asyncio.run(__async_refresh_session())
