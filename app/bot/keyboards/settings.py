from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.back import BackAction
from app.bot.actions.switch_scene import SwitchSceneAction


def get_settings_keyboard(
        i18n: I18nContext,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the settings page.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                # InlineKeyboardButton(
                #     text=i18n.get("button-notifications"),
                #     callback_data=SwitchSceneAction(scene="notifications").pack(),
                # ),
                InlineKeyboardButton(
                    text=i18n.get("button-lang"),
                    callback_data=SwitchSceneAction(scene="language").pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-back"),
                    callback_data=BackAction().pack(),
                )
            ]
        ]
    )
