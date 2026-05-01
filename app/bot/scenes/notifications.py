from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.assets.enums.notification_kind import NotificationKind
from app.assets.models.database import User
from app.bot.actions.toggle_notification import ToggleNotificationAction
from app.bot.keyboards.notifications import get_notifications_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class NotificationsScene(BaseScene, state="notifications"):
    """
    Scene for toggling notification preferences.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user: User,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get("notifications"),
            reply_markup=get_notifications_keyboard(i18n, user.settings),
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened the notifications menu."
        )

    @on.callback_query(ToggleNotificationAction.filter())
    async def on_toggle_notification(
            self,
            callback_query: CallbackQuery,
            callback_data: ToggleNotificationAction,
            user: User,
            database_session: AsyncSession,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        if callback_data.kind == NotificationKind.UPCOMING:
            user.settings.upcoming_class_notifications_enabled = (
                not user.settings.upcoming_class_notifications_enabled
            )
        elif callback_data.kind == NotificationKind.DAILY:
            user.settings.daily_class_notifications_enabled = (
                not user.settings.daily_class_notifications_enabled
            )

        await database_session.commit()

        await user_message.edit(
            i18n.get("notifications"),
            reply_markup=get_notifications_keyboard(i18n, user.settings),
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} toggled '{callback_data.kind}' notifications "
            f"to upcoming={user.settings.upcoming_class_notifications_enabled}, "
            f"daily={user.settings.daily_class_notifications_enabled}."
        )
