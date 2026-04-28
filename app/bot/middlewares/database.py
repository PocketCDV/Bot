from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.assets.controllers.database import DatabaseController


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware which provides database session instance on every bot event handle.
    """

    def __init__(
            self,
            database: DatabaseController,
    ) -> None:
        """
        DatabaseMiddleware Constructor.
        :param database: DatabaseController instance.
        """

        self._database: DatabaseController = database

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Inserts database session instance in workflow data.
        """

        async with self._database.session() as session:
            data["database_session"] = session
            return await handler(event, data)
