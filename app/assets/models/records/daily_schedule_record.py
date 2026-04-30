from datetime import datetime, timedelta
from typing import List, Any, Dict

from aiogram import Bot
from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.records.class_record import ClassRecord


class DailyScheduleRecord(BaseModel):
    """
    Contains a sequence of class records of the same date, represents a single day in a schedule.
    """

    class_records: List[ClassRecord] = Field(default_factory=list)
    """
    Class records of the same date.
    """

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'DailyScheduleRecord':
        """
        Returns a DailyScheduleRecord object from JSON.
        :param data:
        :return:
        """

        return cls(
            class_records=[ClassRecord.from_json(record) for record in data["class_records"]]
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the DailyScheduleRecord object to JSON.
        :return: JSON data.
        """

        return {
            "class_records": [record.to_json() for record in self.class_records],
        }

    async def to_string(
            self,
            bot: Bot,
            i18n: I18nContext,
    ) -> str:
        """
        Converts DailyScheduleRecord object to a string representation.
        :param bot: Bot instance.
        :param i18n: I18n context.
        :return: String representation.
        """

        return "\n\n".join(
            [await record.to_string(bot, i18n) for record in self.class_records]
        )

    def get_active_meeting(
            self,
            time: datetime,
    ) -> ClassRecord | None:
        """
        Returns the class record with valid URL for the current or upcoming online meeting based on the given time.
        Checks if the given time falls within the range of start_time - 30 minutes and end_time.

        :param time: Current time.
        :return: Online meeting or None if no active meeting found.
        """

        for record in self.class_records:
            window_start: datetime = record.start_time - timedelta(minutes=30)

            if record.online_meeting_url and window_start <= time <= record.end_time:
                return record
