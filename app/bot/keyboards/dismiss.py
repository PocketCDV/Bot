from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.dismiss import DismissAction


def get_dismiss_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    """
    Inline keyboard with a single button for dismissing a notification.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-dismiss"),
                    callback_data=DismissAction().pack(),
                )
            ]
        ]
    )
