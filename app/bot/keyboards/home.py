from datetime import datetime, timezone

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.assets.models.class_record import ClassRecord
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.actions.switch_scene import SwitchSceneAction


def get_home_keyboard(
        schedule: ScheduleDayRecord,
        i18n: I18nContext,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the home page.
    :param schedule: Schedule for the home page (For online meeting URL extraction).
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    meeting: ClassRecord | None = schedule.get_active_meeting(datetime.now(timezone.utc))

    if meeting is not None:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get(
                    "button-join-meeting",
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
            text=i18n.get("button-lang"),
            callback_data=SwitchSceneAction(scene="language").pack(),
        )
    )

    return builder.as_markup()
