from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.proceed import ProceedAction


def get_start_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the greeting page.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-proceed"),
                    callback_data=ProceedAction().pack(),
                )
            ]
        ]
    )
