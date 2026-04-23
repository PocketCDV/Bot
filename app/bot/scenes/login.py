import asyncio
from typing import Coroutine, Any

from aiogram import Bot
from aiogram.fsm.scene import Scene, on
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.middlewares.message_id import UserMessage
from config import Config


class LoginScene(Scene, state="login"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            bot: Bot,
            config: Config,
            user_message: UserMessage,
    ) -> None:
        await self._open_login_page(
            bot=bot,
            config=config,
            user_message=user_message,
            delete_message_id=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            bot: Bot,
            config: Config,
            user_message: UserMessage,
    ) -> None:
        await self._open_login_page(
            bot=bot,
            config=config,
            user_message=user_message,
        )

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()

    @staticmethod
    async def _open_login_page(
            bot: Bot,
            config: Config,
            user_message: UserMessage,
            delete_message_id: int | None = None,
    ) -> None:
        login_message_coroutine: Coroutine[Any, Any, None] = user_message.edit_message(
            _("message.login"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("button.login"),
                            web_app=WebAppInfo(url=config.web_app_url),
                        )
                    ]
                ]
            )
        )

        if delete_message_id is not None:
            await asyncio.gather(
                login_message_coroutine,
                bot.delete_message(
                    user_message.user_id,
                    delete_message_id,
                ),
                return_exceptions = True,
            )
        else:
            await login_message_coroutine
