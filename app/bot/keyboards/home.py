from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.assets.models.records.class_record import ClassRecord
from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.bot.actions.switch_scene import SwitchSceneAction
from app.utils import now_local


def get_home_keyboard(
        daily_schedule: DailyScheduleRecord,
        i18n: I18nContext,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the home page.
    :param daily_schedule: Schedule for the home page (For online meeting URL extraction).
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    meeting: ClassRecord | None = daily_schedule.get_active_meeting(now_local())

    if meeting is not None:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get(
                    "button-join-meeting-named",
                    meeting=meeting.title,
                ),
                url=meeting.online_meeting_url,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=i18n.get("button-view-schedule"),
            callback_data=SwitchSceneAction(scene="schedule").pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=i18n.get("button-settings"),
            callback_data=SwitchSceneAction(scene="settings").pack(),
        )
    )

    return builder.as_markup()
