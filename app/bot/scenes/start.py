from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from app.bot.actions.proceed import ProceedAction
from app.bot.keyboards.login import get_login_keyboard
from app.bot.keyboards.start import get_start_keyboard
from app.bot.logging import logger
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene
from app.database.models import User


class StartScene(BaseScene, state="start"):
    """
    Base entry scene, introduction for new users and a home page for logged-in users.
    """

    @on.message.enter()
    async def on_enter(
            self,
            message: Message,
            user: User,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        if user is not None:
            await self.wizard.goto("home")
            return

        await user_message.new(
            i18n.get(
                "greeting",
                first_name=message.from_user.first_name,
            ),
            reply_markup=get_start_keyboard(i18n),
            message_to_delete=message.message_id,
        )

        logger.info(
            f"User {message.from_user.id} opened the greeting page."
        )

    @on.callback_query(ProceedAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get(
                "greeting-login",
            ),
            reply_markup=get_login_keyboard(i18n)
        )
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
