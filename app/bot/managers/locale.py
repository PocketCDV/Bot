from aiogram.types import User as AiogramUser
from aiogram_i18n.managers import BaseManager
from sqlalchemy import update

from app.assets.controllers.database import Database
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
            *,
            event_from_user: AiogramUser | None,
            user: User | None,
    ) -> str | None:
        if user is None:
            return self.default_locale if event_from_user is None else event_from_user.language_code

        return user.locale

    async def set_locale(
            self,
            locale: str,
            event_from_user: AiogramUser | None,
            database: Database,
    ) -> None:
        if event_from_user is None:
            return

        async with database.session_maker() as database_session:
            await database_session.execute(
                update(User)
                .filter_by(telegram_id=event_from_user.id)
                .values(locale=locale)
            )
            await database_session.commit()
