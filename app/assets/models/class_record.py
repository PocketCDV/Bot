from datetime import datetime
from typing import Dict, Any

from aiogram_i18n import I18nContext
from pydantic import BaseModel


class ClassRecord(BaseModel):
    """
    Contains all required information about a class for it to be displayed.
    """

    title: str
    """
    Class title.
    """

    start_time: datetime
    """
    Class start time.
    """

    end_time: datetime
    """
    Class end time.
    """

    room_name: str
    """
    Class room name. Could be 'N.102', 'R.201', etc.
    """

    online_meeting_url: str | None = None
    """
    URL for an online meeting.
    """

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ClassRecord':
        """
        Returns a ClassRecord object from JSON.
        :param data: JSON data.
        :return: ClassRecord object.
        """

        return cls.model_validate(data)

    def to_json(self) -> Dict[str, Any]:
        """
        Converts the ClassRecord object to JSON.
        :return: JSON data.
        """

        return self.model_dump(mode="json")

    def to_string(
            self,
            i18n: I18nContext,
    ) -> str:
        """
        Converts ClassRecord object to a string representation.
        :param i18n: I18n context.
        :return: String representation.
        """

        return i18n.get(
            "schedule-class-entry.short",
            title=self.title,
            start_time=self.start_time.strftime("%H:%M"),
            end_time=self.end_time.strftime("%H:%M"),
            room=self.room_name,
        )
