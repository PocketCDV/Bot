from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.bot.actions.back import BackAction
from app.bot.actions.switch_language import SwitchLanguageAction
from app.bot.enums.locale import Locale
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene


class LanguageScene(BaseScene, state="language"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for locale in Locale:
            builder.row(
                InlineKeyboardButton(
                    text=i18n.get("button-language", language=locale),
                    callback_data=SwitchLanguageAction(locale=Locale(locale)).pack()
                )
            )

        builder.row(
            InlineKeyboardButton(
                text=i18n.get("button-back"),
                callback_data=BackAction().pack()
            )
        )

        await user_message.edit(
            i18n.get("language"),
            reply_markup=builder.as_markup()
        )
        await callback_query.answer()

    @on.callback_query(SwitchLanguageAction.filter())
    async def on_switch_language(
            self,
            callback_query: CallbackQuery,
            callback_data: SwitchLanguageAction,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await i18n.set_locale(callback_data.locale)

        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for locale in Locale:
            builder.row(
                InlineKeyboardButton(
                    text=i18n.get("button-language", language=locale, locale=callback_data.locale),
                    callback_data=SwitchLanguageAction(locale=Locale(locale)).pack()
                )
            )

        builder.row(
            InlineKeyboardButton(
                text=i18n.get("button-back", locale=callback_data.locale),
                callback_data=BackAction().pack()
            )
        )

        await user_message.edit(
            i18n.get("language", locale=callback_data.locale),
            reply_markup=builder.as_markup()
        )
        await callback_query.answer()
