from typing import List, Any, Dict

from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.class_record import ClassRecord


class ScheduleDayRecord(BaseModel):
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
    ) -> 'ScheduleDayRecord':
        """
        Returns a ScheduleDayRecord object from JSON.
        :param data:
        :return:
        """

        return cls(
            class_records=[ClassRecord.from_json(record) for record in data["class_records"]]
        )

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the ScheduleDayRecord object to JSON.
        :return: JSON data.
        """

        return {
            "class_records": [record.to_json() for record in self.class_records],
        }

    def to_string(
            self,
            i18n: I18nContext,
    ) -> str:
        """
        Converts ScheduleDayRecord object to a string representation.
        :param i18n: I18n context.
        :return: String representation.
        """

        return "\n\n".join(
            [record.to_string(i18n) for record in self.class_records]
        )
