from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from app.bot.keyboards.settings import get_settings_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class SettingsScene(BaseScene, state="settings"):
    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get("settings"),
            reply_markup=get_settings_keyboard(i18n),
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened the settings menu."
        )
