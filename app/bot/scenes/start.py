import asyncio

from aiogram import Bot
from aiogram.fsm.scene import on
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.utils.i18n import gettext as _

from app.bot.actions.proceed import ProceedAction
from app.bot.logging import logger
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene
from app.database.models import User
from config import Config


class StartScene(BaseScene, state="start"):
    """
    Base entry scene, introduction for new users and a home page for logged-in users.
    """

    @on.message.enter()
    async def on_enter(
            self,
            message: Message,
            bot: Bot,
            user: User,
            user_message: UserMessage,
    ) -> None:
        if user is not None:
            await self.wizard.goto("home")
            return

        await asyncio.gather(
            user_message.new_message(
                _("message.greeting").format(first_name=message.from_user.first_name),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=_("button.proceed"), callback_data=ProceedAction().pack())
                        ]
                    ]
                ),
            ),
            bot.delete_message(
                message.chat.id,
                message.message_id,
            ),
            return_exceptions=True,
        )

        logger.info(
            f"User {message.from_user.id} opened the greeting page."
        )

    @on.callback_query(ProceedAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
            config: Config,
            user_message: UserMessage,
    ) -> None:
        await user_message.edit_message(
            _("message.greeting.login"),
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
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
