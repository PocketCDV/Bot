from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel


class ClassEntry(BaseModel):
    title: str
    module: str | None = None
    form: str
    start_time: datetime
    end_time: datetime
    term_id: int
    group_id: int
    room: int
    teachers: int
    status: str | None = None

    @classmethod
    def from_data(
            cls,
            data: Dict[str, Any],
    ) -> 'ClassEntry':
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
