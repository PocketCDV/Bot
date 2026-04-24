from typing import Any, Dict

from aiogram.types import User as AiogramUser
from aiogram_i18n.managers import BaseManager
from sqlalchemy import update

from app.database.database import Database
from app.database.models import User


class LocaleManager(BaseManager):
    def __init__(
            self,
            *,
            default_locale: str,
    ) -> None:
        super().__init__(default_locale=default_locale)

    async def get_locale(
            self,
            data: Dict[str, Any],
    ) -> str | None:
        user: User | None = data.get("user")

        if user is None:
            from_user: AiogramUser | None = data.get("event_from_user")
            return self.default_locale if from_user is None else from_user.language_code

        return user.locale

    async def set_locale(
            self,
            locale: str,
            data: Dict[str, Any],
    ) -> None:
        from_user: AiogramUser | None = data.get("event_from_user")

        if from_user is None:
            return

        database: Database = data.get("database")

        async with database.session_maker() as database_session:
            await database_session.execute(
                update(User)
                .filter_by(telegram_id=from_user.id)
                .values(locale=locale)
            )
