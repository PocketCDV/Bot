from datetime import date, datetime, timezone, timedelta
from ssl import SSLContext
from typing import Any, Dict, List, Tuple, Sequence

from aiohttp import ClientSession

from app.assets.models.class_entry import ClassEntry


class APIController:
    TEMP_SESSION_ID: str = "e3f9c4eecdec113f9c3b60b73172c790"

    def __init__(
            self,
            base_url: str,
            *,
            ssl_context: SSLContext | None = None,
    ) -> None:
        self._base_url: str = base_url
        self._ssl_context: SSLContext | None = ssl_context

    async def get_schedule(
            self,
            telegram_id: int,
            start_date: date,
            end_date: date,
    ) -> Sequence[ClassEntry]:
        class_entries: List[ClassEntry] = []

        async with ClientSession() as session:
            async with session.post(
                f"{self._base_url}/ajax.php",
                params={"action": "get-student-plan"},
                data={
                    "poczatek": start_date.strftime("%Y-%m-%d"),
                    "koniec": end_date.strftime("%Y-%m-%d"),
                },
                cookies={"WU_PHPSESSID": self.TEMP_SESSION_ID},
                ssl=self._ssl_context,
            ) as response:
                data: Dict[str, Any] = await response.json()

        if not isinstance(data["error_code"], int) or data["error_code"]:
            raise Exception(f"Error while getting schedule data: {data['error_code']}")

        for data_entry in data["return"]:
            class_entries.append(ClassEntry.from_data(data_entry))

        class_entries.sort(key=lambda entry: entry.start_time)

        return class_entries

    async def get_upcoming_schedule(
            self,
            telegram_id: int,
            *,
            next_days: int | None = None,
    ) -> Sequence[ClassEntry]:
        start_date: date = datetime.now(timezone.utc).date()
        end_date: date = start_date + timedelta(days=(next_days or 0) + 1)

        return await self.get_schedule(
            telegram_id,
            start_date,
            end_date
        )
