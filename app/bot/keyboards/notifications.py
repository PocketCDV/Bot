from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.assets.enums.notification_kind import NotificationKind
from app.assets.models.database import UserSettings
from app.bot.actions.back import BackAction
from app.bot.actions.toggle_notification import ToggleNotificationAction


def get_notifications_keyboard(
        i18n: I18nContext,
        settings: UserSettings,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the notifications page.
    :param i18n: I18n context.
    :param settings: User's current notification settings, drives toggle labels.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get(
                        "button-toggle-upcoming-notifications",
                        enabled=str(settings.upcoming_class_notifications_enabled).lower(),
                    ),
                    callback_data=ToggleNotificationAction(kind=NotificationKind.UPCOMING).pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get(
                        "button-toggle-daily-notifications",
                        enabled=str(settings.daily_class_notifications_enabled).lower(),
                    ),
                    callback_data=ToggleNotificationAction(kind=NotificationKind.DAILY).pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-back"),
                    callback_data=BackAction().pack(),
                )
            ]
        ]
    )
