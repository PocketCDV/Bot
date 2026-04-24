from datetime import date, datetime, timezone, timedelta
from typing import Dict, Any, Tuple

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import on
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_record import ScheduleRecord
from app.bot.actions.back import BackAction
from app.bot.actions.flip_page import FlipPageAction
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene


class ScheduleScene(BaseScene, state="schedule"):
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
        schedule_date = initial_date or datetime.now(timezone.utc).date()
        start_date, end_date = self._get_week_range_by_date(schedule_date)

        schedule: ScheduleRecord = await schedule_controller.get_schedule(
            start_date,
            end_date,
            session_id,
        )

        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-flip-page.backwards"),
                        callback_data=FlipPageAction.backwards().pack(),
                    ),
                    InlineKeyboardButton(
                        text=i18n.get("button-flip-page.forwards"),
                        callback_data=FlipPageAction.forwards().pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-back"),
                        callback_data=BackAction().pack(),
                    )
                ]
            ]
        )

        if schedule_date in schedule.schedule:
            await user_message.edit_message(
                i18n.get(
                    "schedule",
                    weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                    schedule_date=schedule_date.strftime("%d.%m.%Y"),
                    schedule=schedule.to_string(schedule_date, i18n),
                ),
                reply_markup=reply_markup,
            )
        else:
            await user_message.edit_message(
                i18n.get(
                    "schedule-no-classes",
                    weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                    schedule_date=schedule_date.strftime("%d.%m.%Y"),
                ),
                reply_markup=reply_markup,
            )

        await callback_query.answer()

        await state.update_data(
            schedule_date=schedule_date.isoformat(),
            schedule=schedule.to_json(),
            fetched_start=start_date.isoformat(),
            fetched_end=end_date.isoformat(),
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
        data: Dict[str, Any] = await state.get_data()

        schedule_date: date = date.fromisoformat(data.get("schedule_date"))
        schedule: ScheduleRecord = ScheduleRecord.from_json(data.get("schedule"))
        fetched_start: date = date.fromisoformat(data.get("fetched_start"))
        fetched_end: date = date.fromisoformat(data.get("fetched_end"))

        schedule_date += timedelta(days=callback_data.offset)

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

        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-flip-page.backwards"),
                        callback_data=FlipPageAction.backwards().pack(),
                    ),
                    InlineKeyboardButton(
                        text=i18n.get("button-flip-page.forwards"),
                        callback_data=FlipPageAction.forwards().pack(),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-back"),
                        callback_data=BackAction().pack(),
                    )
                ]
            ]
        )

        if schedule_date in schedule.schedule:
            await user_message.edit_message(
                i18n.get(
                    "schedule",
                    weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                    schedule_date=schedule_date.strftime("%d.%m.%Y"),
                    schedule=schedule.to_string(schedule_date, i18n),
                ),
                reply_markup=reply_markup,
            )
        else:
            await user_message.edit_message(
                i18n.get(
                    "schedule-no-classes",
                    weekday=i18n.get("weekday", weekday=schedule_date.weekday()),
                    schedule_date=schedule_date.strftime("%d.%m.%Y"),
                ),
                reply_markup=reply_markup,
            )

        await callback_query.answer()

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
