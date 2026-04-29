from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel


class ClassEntry(BaseModel):
    """
    WU Model of a class entry, contains everything WU provides about each class.
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

    room: int
    """
    Class room ID.
    """

    teachers: int
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
    ) -> 'ClassEntry':
        """
        Returns a ClassEntry object from raw WU Data.
        :param data: Data from WU.
        :return: ClassEntry object.
        """

        return cls(
            title=data.get("title"),
            module=data.get("module"),
            form=data.get("form"),
            status=data.get("status"),
            start_time=data.get("start"),
            end_time=data.get("end"),
            room=data.get("room"),
            teachers=data.get("teachers"),
            hangout_link=data.get("hangoutLink").replace("\\/", "/") if data.get("hangoutLink") else None,
        )

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ClassEntry':
        """
        Returns ClassEntry object from JSON.
        :param data: JSON data.
        :return: ClassEntry object.
        """

        return cls.model_validate(data)

    def to_json(self) -> Dict[str, Any]:
        """
        Converts ClassEntry object to JSON.
        :return: JSON data.
        """

        return self.model_dump(mode="json")
