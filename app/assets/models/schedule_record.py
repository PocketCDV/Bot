from datetime import date
from typing import Dict, Any

from aiogram import Bot
from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.schedule_day_record import ScheduleDayRecord


class ScheduleRecord(BaseModel):
    """
    Contains a mapping of dates to ScheduleDayRecord objects,
    represents a day-separated schedule on a range of dates.
    """

    schedule: Dict[date, ScheduleDayRecord] = Field(default_factory=dict)
    """
    Mapping of dates to ScheduleDayRecord objects.
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
            schedule={date.fromisoformat(schedule_date): ScheduleDayRecord.from_json(record)
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
        Converts ScheduleDayRecord object selected by a date to a string representation.
        If date is not present in schedule, returns an empty string.

        :param schedule_date: Date for ScheduleDayRecord.
        :param bot: Bot instance.
        :param i18n: I18n context.
        :return: String representation.
        """

        schedule_day: ScheduleDayRecord | None = self.schedule.get(schedule_date)

        if schedule_day is None:
            return ""

        return await schedule_day.to_string(bot, i18n)
