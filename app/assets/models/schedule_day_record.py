from typing import List, Any, Dict

from aiogram_i18n import I18nContext
from pydantic import BaseModel, Field

from app.assets.models.class_record import ClassRecord


class ScheduleDayRecord(BaseModel):
    class_records: List[ClassRecord] = Field(default_factory=list)

    @classmethod
    def from_json(
            cls,
            data: Dict[str, Any],
    ) -> 'ScheduleDayRecord':
        return cls(
            class_records=[ClassRecord.from_json(record) for record in data["class_records"]]
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            "class_records": [record.to_json() for record in self.class_records],
        }

    def to_string(
            self,
            i18n: I18nContext,
    ) -> str:
        return "\n\n".join(
            [record.to_string(i18n) for record in self.class_records]
        )
