from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.back import BackAction
from app.bot.actions.flip_page import FlipPageAction


def get_detail_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the detailed class info page.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-back"),
                    callback_data=BackAction().pack(),
                )
            ]
        ]
    )
