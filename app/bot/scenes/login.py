from aiogram.fsm.scene import on
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from aiogram_i18n import I18nContext

from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene
from config import Config


class LoginScene(BaseScene, state="login"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            config: Config,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.new_message(
            i18n.get("login"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=i18n.get("button-login"),
                            web_app=WebAppInfo(url=config.web_app_url),
                        )
                    ]
                ]
            ),
            message_to_delete=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            config: Config,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit_message(
            i18n.get("login"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=i18n.get("button-login"),
                            web_app=WebAppInfo(url=config.web_app_url),
                        )
                    ]
                ]
            ),
        )
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
