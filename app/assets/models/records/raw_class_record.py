from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel


class RawClassRecord(BaseModel):
    """
    WU Model of a class entry, contains everything WU provides about each class.
    """

    class_id: int
    """
    Class ID.
    """

    title: str
    """
    Class title.
    """

    module: str | None = None
    """
    Class module. May be ``None`` when WU does not assign a module to the class.
    """

    form: str
    """
    Class form, could be 'Laboratory', 'Lecture' etc.
    """

    status: str | None = None
    """
    Class status. Could be 'REGULAR', 'CANCELLED' etc.
    """

    start_time: datetime
    """
    Start time of the class.
    """

    end_time: datetime
    """
    End time of the class.
    """

    room_id: int
    """
    Class room ID.
    """

    teacher_id: int
    """
    Teacher ID.
    """

    hangout_link: str | None = None
    """
    URL for an online meeting.
    """

    @classmethod
    def from_data(
            cls,
            data: Dict[str, Any],
    ) -> 'RawClassRecord':
        """
        Returns a RawClassRecord object from raw WU Data.
        :param data: Data from WU.
        :return: RawClassRecord object.
        """

        return cls(
            class_id=data.get("term_id"),
            title=data.get("title"),
            module=data.get("module"),
            form=data.get("form"),
            status=data.get("status"),
            start_time=data.get("start"),
            end_time=data.get("end"),
            room_id=data.get("room"),
            teacher_id=data.get("teachers"),
            hangout_link=data.get("hangoutLink").replace("\\/", "/") if data.get("hangoutLink") else None,
        )

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'RawClassRecord':
        """
        Returns RawClassRecord object from JSON.
        :param data: JSON data.
        :return: RawClassRecord object.
        """

        return cls.model_validate(data)

    def to_json(self) -> Dict[str, Any]:
        """
        Converts RawClassRecord object to JSON.
        :return: JSON data.
        """

        return self.model_dump(mode="json")
