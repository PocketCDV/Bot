from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.bot.actions.back import BackAction
from app.bot.actions.flip_page import FlipPageAction


def get_schedule_keyboard(i18n: I18nContext) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=i18n.get("button-flip-page.backwards"),
                    callback_data=FlipPageAction.backwards().pack(),
                ),
                InlineKeyboardButton(
                    text=i18n.get("button-flip-page.forwards"),
                    callback_data=FlipPageAction.forwards().pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=i18n.get("button-back"),
                    callback_data=BackAction().pack(),
                )
            ]
        ]
    )
