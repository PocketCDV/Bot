from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.bot.actions.back import BackAction
from app.bot.actions.switch_language import SwitchLanguageAction
from app.assets.enums.language import Language


def get_language_keyboard(
        i18n: I18nContext,
        *,
        locale: Language | None = None,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the language select page.
    :param i18n: I18n context.
    :param locale: Locale to use when localizing response.
    :return: InlineKeyboardMarkup.
    """

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for language in Language:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get("button-language", language=language, locale=locale),
                callback_data=SwitchLanguageAction(language=Language(language)).pack()
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=i18n.get("button-back", locale=locale),
            callback_data=BackAction().pack()
        )
    )

    return builder.as_markup()
