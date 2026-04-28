from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserMiddleware(BaseMiddleware):
    """
    Middleware which provides user object from database on every user-related event.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Inserts database user object in workflow data.
        """

        from_user: User | None = data.get("event_from_user")

        if from_user is None:
            return await handler(event, data)

        database_session: AsyncSession = data.get("database_session")

        if database_session is None:
            raise Exception(
                "Missing database session. DatabaseMiddleware was probably registered after UserMiddleware"
            )

        user: User | None = await database_session.scalar(
            select(User)
            .filter_by(telegram_id=from_user.id).limit(1)
        )

        data["user"] = user
        return await handler(event, data)
