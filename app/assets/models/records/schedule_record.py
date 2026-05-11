from datetime import date
from typing import Dict, Any

from aiogram import Bot
from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.records.daily_schedule_record import DailyScheduleRecord


class ScheduleRecord(BaseModel):
    """
    Contains a mapping of dates to DailyScheduleRecord objects,
    represents a day-separated schedule on a range of dates.
    """

    schedule: Dict[date, DailyScheduleRecord] = Field(default_factory=dict)
    """
    Mapping of dates to DailyScheduleRecord objects.
    """

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ScheduleRecord':
        """
        Returns a ScheduleRecord object from JSON.
        :param data:
        :return:
        """

        return ScheduleRecord(
            schedule={date.fromisoformat(schedule_date): DailyScheduleRecord.from_json(record)
                      for schedule_date, record in data.get("schedule").items()},
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the ScheduleRecord object to JSON.
        :return: JSON data.
        """

        return {
            "schedule": {schedule_date.isoformat(): record.to_json()
                         for schedule_date, record in self.schedule.items()},
        }

    async def to_string(
            self,
            schedule_date: date,
            bot: Bot,
            i18n: I18nContext,
    ) -> str | None:
        """
        Converts DailyScheduleRecord object selected by a date to a string representation.
        If date is not present in schedule, returns an empty string.

        :param schedule_date: Date for DailyScheduleRecord.
        :param bot: Bot instance.
        :param i18n: I18n context.
        :return: String representation.
        """

        daily_schedule: DailyScheduleRecord | None = self.schedule.get(schedule_date)

        if daily_schedule is None:
            return ""

        return await daily_schedule.to_string(bot, i18n)
