from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram_i18n import I18nContext

from config import config


def get_login_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the login page.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-login"),
                    web_app=WebAppInfo(url=config.web_app_url),
                )
            ]
        ]
    )
