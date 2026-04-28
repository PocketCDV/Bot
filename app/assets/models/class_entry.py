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

    module: str | None = None
    """
    Class module.
    """

    form: str
    """
    Class form, could be 'Laboratory', 'Lecture' etc.
    """

    start_time: datetime
    """
    Start time of the class.
    """

    end_time: datetime
    """
    End time of the class.
    """

    term_id: int
    """
    Class ID.
    """

    group_id: int
    """
    User's group ID.
    """

    room: int
    """
    Class room ID.
    """

    teachers: int
    """
    Teacher ID.
    """

    status: str | None = None
    """
    Class status. Could be 'REGULAR', 'CANCELLED' etc.
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
            title=data["title"],
            module=data.get("module"),
            form=data["form"],
            start_time=data["start"],
            end_time=data["end"],
            term_id=data["term_id"],
            group_id=data["group_id"],
            room=data["room"],
            teachers=data["teachers"],
            status=data.get("status"),
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
