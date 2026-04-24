from datetime import date
from typing import Dict, Any

from aiogram.utils.i18n import I18n
from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.schedule_day_record import ScheduleDayRecord


class ScheduleRecord(BaseModel):
    schedule: Dict[date, ScheduleDayRecord] = Field(default_factory=dict)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ScheduleRecord':
        return ScheduleRecord(
            schedule={date.fromisoformat(schedule_date): ScheduleDayRecord.from_json(record)
                      for schedule_date, record in data.get("schedule").items()},
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "schedule": {schedule_date.isoformat(): record.to_json()
                         for schedule_date, record in self.schedule.items()},
        }

    def to_string(
            self,
            schedule_date: date,
            i18n: I18nContext,
    ) -> str | None:
        schedule_day: ScheduleDayRecord | None = self.schedule.get(schedule_date)

        if schedule_day is not None:
            return schedule_day.to_string(i18n)
