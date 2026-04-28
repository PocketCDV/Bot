from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from app.bot.actions.switch_language import SwitchLanguageAction
from app.bot.keyboards.language import get_language_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class LanguageScene(BaseScene, state="language"):
    """
    Scene for switching bot's language.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get("language"),
            reply_markup=get_language_keyboard(i18n),
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened the language select menu."
        )

    @on.callback_query(SwitchLanguageAction.filter())
    async def on_switch_language(
            self,
            callback_query: CallbackQuery,
            callback_data: SwitchLanguageAction,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await i18n.set_locale(callback_data.language)

        await user_message.edit(
            i18n.get("language", language=callback_data.language),
            reply_markup=get_language_keyboard(i18n, locale=callback_data.language),
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} set language to '{callback_data.language}'"
        )
