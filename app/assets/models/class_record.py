from datetime import datetime
from typing import Dict, Any

from aiogram_i18n import I18nContext
from pydantic import BaseModel


class ClassRecord(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    room_name: str

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ClassRecord':
        return cls(
            title=data.get("title"),
            start_time=datetime.fromisoformat(data.get("start_time")),
            end_time=datetime.fromisoformat(data.get("end_time")),
            room_name=data.get("room_name"),
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "room_name": self.room_name,
        }

    def to_string(
            self,
            i18n: I18nContext,
    ) -> str:
        return i18n.get(
            "schedule-class-entry",
            title=self.title,
            start_time=self.start_time.strftime("%H:%M"),
            end_time=self.end_time.strftime("%H:%M"),
            room=self.room_name,
        )
