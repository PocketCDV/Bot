from datetime import date, datetime, timezone, timedelta
from typing import Dict, Any, Tuple

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery
from aiogram_i18n import I18nContext

from app.asgi.logger import logger
from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_record import ScheduleRecord
from app.bot.actions.flip_page import FlipPageAction
from app.bot.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.schedule import get_schedule_keyboard
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


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
            i18n: I18nContext,
            schedule_controller: ScheduleController,
            initial_date: date | None = None,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            schedule_date = initial_date or datetime.now(timezone.utc).date()

            start_date, end_date = self._get_week_range_by_date(schedule_date)
            schedule: ScheduleRecord = await schedule_controller.get_schedule(
                start_date,
                end_date,
                session_id,
            )
        except InvalidSessionError:
            await user_message.edit_login(i18n)
            await self.wizard.exit()
            return

        await self._render_schedule(schedule_date, schedule, user_message, i18n)
        await self._save_state(state, schedule_date, schedule, start_date, end_date)
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened daily schedule."
        )

    @on.callback_query(FlipPageAction.filter())
    async def on_flip_page(
            self,
            callback_query: CallbackQuery,
            callback_data: FlipPageAction,
            state: FSMContext,
            user_message: UserMessage,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            data: Dict[str, Any] = await state.get_data()

            schedule_date: date = date.fromisoformat(data["schedule_date"]) + timedelta(days=callback_data.offset)
            schedule: ScheduleRecord = ScheduleRecord.from_json(data["schedule"])
            fetched_start: date = date.fromisoformat(data["fetched_start"])
            fetched_end: date = date.fromisoformat(data["fetched_end"])

            if not (fetched_start <= schedule_date <= fetched_end):
                start_date, end_date = self._get_week_range_by_date(schedule_date)
                new_schedule: ScheduleRecord = await schedule_controller.get_schedule(
                    start_date,
                    end_date,
                    session_id,
                )

                schedule.schedule.update(new_schedule.schedule)

                fetched_start = min(fetched_start, start_date)
                fetched_end = max(fetched_end, end_date)
        except InvalidSessionError:
            await user_message.edit_login(i18n)
            await self.wizard.exit()
            return

        await self._render_schedule(schedule_date, schedule, user_message, i18n)
        await self._save_state(state, schedule_date, schedule, fetched_start, fetched_end)
        await callback_query.answer()

    @staticmethod
    def _get_week_range_by_date(d: date) -> Tuple[date, date]:
        start: date = d - timedelta(days=d.weekday())
        end: date = start + timedelta(days=6)
        return start, end

    @staticmethod
    async def _render_schedule(
            schedule_date: date,
            schedule: ScheduleRecord,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        """
        Display schedule using current schedule date, ScheduleRecord object and user message data.
        :param schedule_date: Current schedule data.
        :param schedule: ScheduleRecord instance.
        :param user_message: UserMessage instance.
        :param i18n: I18n context.
        """

        if schedule_date in schedule.schedule:
            text: str = i18n.get(
                "schedule",
                weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                schedule_date=schedule_date.strftime("%d.%m.%Y"),
                schedule=schedule.to_string(schedule_date, i18n),
            )
        else:
            text: str = i18n.get(
                "schedule-no-classes",
                weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                schedule_date=schedule_date.strftime("%d.%m.%Y"),
            )

        await user_message.edit(text, reply_markup=get_schedule_keyboard(i18n))

    @staticmethod
    async def _save_state(
            state: FSMContext,
            schedule_date: date,
            schedule: ScheduleRecord,
            fetched_start: date,
            fetched_end: date,
    ) -> None:
        """
        Saves fetched state about all scheduled classes and visited date range.
        :param state: FSMContext instance.
        :param schedule_date: Current schedule data.
        :param schedule: ScheduleRecord instance.
        :param fetched_start: Start date of visited date range.
        :param fetched_end: End date of visited date range.
        """

        await state.update_data(
            schedule_date=schedule_date.isoformat(),
            schedule=schedule.to_json(),
            fetched_start=fetched_start.isoformat(),
            fetched_end=fetched_end.isoformat(),
        )
