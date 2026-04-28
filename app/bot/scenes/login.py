from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from app.bot.keyboards.login import get_login_keyboard
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene


class LoginScene(BaseScene, state="login"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.new(
            i18n.get("login"),
            reply_markup=get_login_keyboard(i18n),
            message_to_delete=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get("login"),
            reply_markup=get_login_keyboard(i18n),
        )
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
