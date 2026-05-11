from aiogram.types import User as AiogramUser
from aiogram_i18n.managers import BaseManager
from sqlalchemy import select, update

from app.assets.controllers.database import DatabaseController
from app.assets.models.database import User, UserSettings


class LocaleManager(BaseManager):
    """
    Manager for retrieving user's locale from database.
    """

    def __init__(
            self,
            *,
            default_locale: str,
    ) -> None:
        """
        LocaleManager Constructor.
        :param default_locale: Default locale to use if user's locale is absent or invalid.
        """

        super().__init__(default_locale=default_locale)

    async def get_locale(
            self,
            *,
            event_from_user: AiogramUser | None,
            user: User | None,
    ) -> str | None:
        """
        Retrieves locale from database.
        :param event_from_user: User info from Aiogram.
        :param user: Database user.
        :return: Retrieved locale.
        """

        if user is None:
            return self.default_locale if event_from_user is None else event_from_user.language_code

        return user.settings.locale if user.settings else None

    async def set_locale(
            self,
            locale: str,
            event_from_user: AiogramUser | None,
            database: DatabaseController,
    ) -> None:
        """
        Updates locale in database.
        :param locale: New locale value.
        :param event_from_user: User info from Aiogram.
        :param database: Database instance.
        """

        if event_from_user is None:
            return

        async with database.session() as database_session:
            await database_session.execute(
                update(UserSettings)
                .where(
                    UserSettings.user_id == select(User.id)
                    .filter_by(telegram_id=event_from_user.id)
                    .scalar_subquery()
                )
                .values(locale=locale)
            )
            await database_session.commit()
