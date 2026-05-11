from datetime import date, timedelta
from typing import Dict, Any, Tuple

from aiogram import Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, Message
from aiogram.utils.payload import decode_payload
from aiogram_i18n import I18nContext

from app.asgi.logger import logger
from app.assets.controllers.schedule import ScheduleController
from app.assets.models.records.class_record import ClassRecord
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.assets.models.records.schedule_record import ScheduleRecord
from app.bot.actions.flip_page import FlipPageAction
from app.assets.enums.payload_action import PayloadAction
from app.assets.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.schedule import get_schedule_keyboard
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene
from app.utils import today_local


class ScheduleScene(BaseScene, state="schedule"):
    """
    Scene for displaying a paginated daily schedule. Retrieves schedule per-week and caches fetched results.
    """

    @on.callback_query.enter()
    async def on_enter(
            self,
            callback_query: CallbackQuery,
            state: FSMContext,
            user_message: UserMessage,
            session_id: str,
            bot: Bot,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
            initial_date: date | None = None,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            schedule_date: date = initial_date or today_local()
            start_date, end_date = self._get_week_range_by_date(schedule_date)
            schedule: ScheduleRecord = await schedule_controller.get_schedule(start_date, end_date, session_id)
        except InvalidSessionError:
            await user_message.ask_to_log_in(i18n)
            await self.wizard.exit()
            return

        await self._display_schedule_page(
            schedule_date,
            schedule,
            start_date,
            end_date,
            user_message,
            bot,
            state,
            i18n,
        )
        await callback_query.answer()

        logger.info(f"User {callback_query.from_user.id} opened daily schedule.")

    @on.callback_query(FlipPageAction.filter())
    async def on_flip_page(
            self,
            callback_query: CallbackQuery,
            callback_data: FlipPageAction,
            state: FSMContext,
            user_message: UserMessage,
            session_id: str,
            bot: Bot,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            data: Dict[str, Any] = await state.get_data()
            schedule_date, schedule, fetched_start, fetched_end = await self._resolve_flip_page(
                data, callback_data.offset, session_id, schedule_controller
            )
        except InvalidSessionError:
            await user_message.ask_to_log_in(i18n)
            await self.wizard.exit()
            return

        await self._display_schedule_page(
            schedule_date,
            schedule,
            fetched_start,
            fetched_end,
            user_message,
            bot,
            state,
            i18n,
        )
        await callback_query.answer()

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

        data: Dict[str, Any] = await state.get_data()

        schedule_date: date = date.fromisoformat(data["schedule_date"])
        daily_schedule: DailyScheduleRecord | None = ScheduleRecord.from_json(data["schedule"]).schedule.get(schedule_date)
        class_record: ClassRecord | None = None

        for class_record in daily_schedule.class_records:
            if class_record.class_id == class_id:
                break

        if class_record is None:
            return

        await self.wizard.goto("detail", class_record=class_record)

    async def _resolve_flip_page(
            self,
            data: Dict[str, Any],
            offset: int,
            session_id: str,
            schedule_controller: ScheduleController,
    ) -> Tuple[date, ScheduleRecord, date, date]:
        """
        Resolves the new schedule date and fetches missing data if the new date is outside the cached range.
        :return: Tuple of (schedule_date, schedule, fetched_start, fetched_end).
        """

        schedule_date: date = date.fromisoformat(data["schedule_date"]) + timedelta(days=offset)
        schedule: ScheduleRecord = ScheduleRecord.from_json(data["schedule"])
        fetched_start: date = date.fromisoformat(data["fetched_start"])
        fetched_end: date = date.fromisoformat(data["fetched_end"])

        if not (fetched_start <= schedule_date <= fetched_end):
            start_date, end_date = self._get_week_range_by_date(schedule_date)
            new_schedule: ScheduleRecord = await schedule_controller.get_schedule(start_date, end_date, session_id)
            schedule.schedule.update(new_schedule.schedule)
            fetched_start = min(fetched_start, start_date)
            fetched_end = max(fetched_end, end_date)

        return schedule_date, schedule, fetched_start, fetched_end

    @staticmethod
    async def _display_schedule_page(
            schedule_date: date,
            schedule: ScheduleRecord,
            fetched_start: date,
            fetched_end: date,
            user_message: UserMessage,
            bot: Bot,
            state: FSMContext,
            i18n: I18nContext,
    ) -> None:
        """
        Displays the schedule for the given date and saves state.
        :param schedule_date: Date to display.
        :param schedule: ScheduleRecord instance.
        :param fetched_start: Start of the cached date range.
        :param fetched_end: End of the cached date range.
        :param user_message: UserMessage instance.
        :param bot: Bot instance.
        :param state: FSMContext instance.
        :param i18n: I18n context.
        """

        if schedule_date in schedule.schedule:
            text: str = i18n.get(
                "schedule",
                weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                schedule_date=schedule_date.strftime("%d.%m.%Y"),
                schedule=await schedule.to_string(schedule_date, bot, i18n),
            )
        else:
            text: str = i18n.get(
                "schedule-no-classes",
                weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                schedule_date=schedule_date.strftime("%d.%m.%Y"),
            )

        await user_message.edit(text, reply_markup=get_schedule_keyboard(i18n))
        await state.update_data(
            schedule_date=schedule_date.isoformat(),
            schedule=schedule.to_json(),
            fetched_start=fetched_start.isoformat(),
            fetched_end=fetched_end.isoformat(),
        )

    @staticmethod
    def _get_week_range_by_date(d: date) -> Tuple[date, date]:
        start: date = d - timedelta(days=d.weekday())
        end: date = start + timedelta(days=6)
        return start, end
