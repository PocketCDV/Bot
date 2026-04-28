from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.switch_scene import SwitchSceneAction


def get_home_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the home page.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-view-schedule"),
                    callback_data=SwitchSceneAction(scene="schedule").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("button-lang"),
                    callback_data=SwitchSceneAction(scene="language").pack(),
                )
            ],
        ]
    )


