from aiogram import Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.payload import decode_payload
from aiogram_i18n import I18nContext

from app.assets.controllers.schedule import ScheduleController
from app.assets.models.records.class_record import ClassRecord
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.assets.enums import PayloadAction
from app.assets.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.home import get_home_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class HomeScene(BaseScene, state="home"):
    """
    Home page scene. Displays today's classes, updates every 10 minutes.
    """

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            bot: Bot,
            state: FSMContext,
            schedule_controller: ScheduleController,
            session_id: str,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            await self._display_home_page(
                message.from_user.first_name,
                bot,
                state,
                schedule_controller,
                session_id,
                user_message,
                i18n,
                message_to_delete=message.message_id,
            )
        except InvalidSessionError:
            await user_message.ask_to_log_in(i18n)
            await self.wizard.exit()
            return

        logger.info(
            f"User {message.from_user.id} opened the home page."
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            bot: Bot,
            state: FSMContext,
            schedule_controller: ScheduleController,
            session_id: str,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            await self._display_home_page(
                callback_query.from_user.first_name,
                bot,
                state,
                schedule_controller,
                session_id,
                user_message,
                i18n,
            )
        except InvalidSessionError:
            await user_message.ask_to_log_in(i18n)
            await self.wizard.exit()
            return

        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened the home page."
        )

    @on.message(CommandStart(deep_link=True))
    async def on_start(
            self,
            message: Message,
            command: CommandObject,
            state: FSMContext,
    ) -> None:
        await message.delete()

        payload: str = decode_payload(command.args)
        action, payload_data = payload.split(":")

        if action != PayloadAction.DETAIL:
            return

        class_id: int = int(payload_data)
        daily_schedule: DailyScheduleRecord = DailyScheduleRecord.from_json(await state.get_value("schedule"))
        class_record: ClassRecord | None = None

        for class_record in daily_schedule.class_records:
            if class_record.class_id == class_id:
                break

        if class_record is None:
            return

        await self.wizard.goto("detail", class_record=class_record)

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()

    @staticmethod
    async def _display_home_page(
            first_name: str,
            bot: Bot,
            state: FSMContext,
            schedule_controller: ScheduleController,
            session_id: str,
            user_message: UserMessage,
            i18n: I18nContext,
            *,
            message_to_delete: int | None = None,
    ) -> None:
        """
        Display home page information.
        """

        daily_schedule: DailyScheduleRecord = await schedule_controller.get_home_schedule(session_id)

        if daily_schedule.class_records:
            text: str = i18n.get(
                "home",
                first_name=first_name,
                classes=await daily_schedule.to_string(bot, i18n),
            )
        else:
            text: str = i18n.get(
                "home-no-classes",
                first_name=first_name,
            )

        if message_to_delete is not None:
            await user_message.new(
                text,
                reply_markup=get_home_keyboard(daily_schedule, i18n),
                message_to_delete=message_to_delete,
            )
        else:
            await user_message.edit(
                text,
                reply_markup=get_home_keyboard(daily_schedule, i18n),
            )

        await state.update_data(schedule=daily_schedule.to_json())
