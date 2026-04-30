from datetime import datetime
from typing import Dict, Any, Mapping

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link
from aiogram_i18n import I18nContext
from pydantic import BaseModel

from app.assets.models.records.raw_class_record import RawClassRecord
from app.assets.enums.payload_action import PayloadAction


class ClassRecord(BaseModel):
    """
    Contains all required information about a class for it to be displayed.
    """

    class_id: int
    """
    Class ID.
    """

    title: str
    """
    Class title.
    """

    module: str
    """
    Class module.
    """

    form: str
    """
    Class form, could be 'Laboratory', 'Lecture' etc.
    """

    start_time: datetime
    """
    Class start time.
    """

    end_time: datetime
    """
    Class end time.
    """

    room_id: int
    """
    Class room ID.
    """

    room_name: str
    """
    Class room name. Could be 'N.102', 'R.201', etc.
    """

    teacher_id: int
    """
    Teacher ID.
    """

    teacher_name: str
    """
    Teacher full name.
    """

    online_meeting_url: str | None = None
    """
    URL for an online meeting.
    """

    is_cancelled: bool = False

    @classmethod
    def from_entry(
            cls,
            raw_class_record: RawClassRecord,
            room_names: Mapping[int, str],
            teacher_names: Mapping[int, str],
    ) -> 'ClassRecord':
        """
        Returns a ClassRecord object from RawClassRecord object and mappings for room and teacher names.
        :param raw_class_record: RawClassRecord object.
        :param room_names: Mapping of room IDs to names.
        :param teacher_names: Mapping of teacher IDs to names.
        :return: ClassRecord object.
        """

        return cls(
            class_id=raw_class_record.class_id,
            title=raw_class_record.title,
            module=raw_class_record.module,
            form=raw_class_record.form,
            start_time=raw_class_record.start_time,
            end_time=raw_class_record.end_time,
            room_id=raw_class_record.room_id,
            room_name=room_names.get(raw_class_record.room_id, "Unknown room"),
            teacher_name=teacher_names.get(raw_class_record.teacher_id, "Unknown lecturer"),
            teacher_id=raw_class_record.teacher_id,
            online_meeting_url=raw_class_record.hangout_link,
            is_cancelled=raw_class_record.status == "CANCELLED",
        )

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

    async def to_string(
            self,
            bot: Bot,
            i18n: I18nContext,
    ) -> str:
        """
        Converts ClassRecord object to a string representation.
        :param bot: Bot instance.
        :param i18n: I18n context.
        :return: String representation.
        """

        return i18n.get(
            "schedule-class-entry.short",
            title=self.title,
            start_time=self.start_time.strftime("%H:%M"),
            end_time=self.end_time.strftime("%H:%M"),
            room=self.room_name,
            detail=await create_start_link(
                bot,
                payload=f"{PayloadAction.DETAIL}:{self.class_id}",
                encode=True,
            )
        )
