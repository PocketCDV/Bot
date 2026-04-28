from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram_i18n import I18nContext

from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.home import get_home_keyboard
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene


class HomeScene(BaseScene, state="home"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user_message: UserMessage,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        if session_id is None:
            await self.wizard.goto("login")
            return

        try:
            text, keyboard = await self._get_schedule_content(
                message.from_user.first_name, session_id, i18n, schedule_controller
            )
        except InvalidSessionError:
            await self.wizard.goto("login")
            return

        await user_message.new(
            text,
            reply_markup=keyboard,
            message_to_delete=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        if session_id is None:
            await self.wizard.goto("login")
            return

        text, keyboard = await self._get_schedule_content(
            callback_query.from_user.first_name, session_id, i18n, schedule_controller
        )

        await user_message.edit(
            text,
            reply_markup=keyboard,
        )
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()

    @staticmethod
    async def _get_schedule_content(
            first_name: str,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> tuple[str, InlineKeyboardMarkup]:
        schedule: ScheduleDayRecord = await schedule_controller.get_home_schedule(session_id)

        if schedule.class_records:
            text: str = i18n.get("home", first_name=first_name, classes=schedule.to_string(i18n))
        else:
            text: str = i18n.get("home-no-classes", first_name=first_name)

        return text, get_home_keyboard(i18n)
