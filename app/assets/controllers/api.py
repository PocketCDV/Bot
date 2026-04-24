from datetime import date
from ssl import SSLContext
from typing import Any, Dict, List, Sequence

from aiohttp import ClientSession, ClientTimeout

from app.assets.models.class_entry import ClassEntry


class APIController:
    def __init__(
            self,
            base_url: str,
            *,
            ssl_context: SSLContext | None = None,
    ) -> None:
        self._base_url: str = base_url
        self._ssl_context: SSLContext | None = ssl_context

    async def get_session_id(
            self,
            login: str,
            password: str,
    ) -> str | None:
        async with ClientSession() as session:
            async with session.post(
                f"{self._base_url}/?login=1",
                data={
                    "login": login,
                    "password": password,
                    "redirectUrl": "https://wu.cdv.pl?page=Main",
                },
                allow_redirects=False,
                ssl=self._ssl_context,
                timeout=ClientTimeout(total=10),
            ) as response:
                return response.cookies.get("WU_PHPSESSID").value

    async def refresh_session_id(
            self,
            session_id: str,
    ) -> str | None:
        async with ClientSession() as session:
            async with session.get(
                f"{self._base_url}/ajax.php",
                params={"action": "get-translations"},
                cookies={"WU_PHPSESSID": session_id},
                ssl=self._ssl_context,
            ) as response:
                try:
                    if response.status == 200 and not int((await response.json())["error_code"]):
                        return response.cookies.get("WU_PHPSESSID").value
                    else:
                        return None
                except TypeError | ValueError:
                    return None

    async def get_schedule(
            self,
            session_id: str,
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
                cookies={"WU_PHPSESSID": session_id},
                ssl=self._ssl_context,
            ) as response:
                data: Dict[str, Any] = await response.json()

        if not isinstance(data["error_code"], int) or data["error_code"]:
            raise Exception(f"Error while getting schedule data: {data['error_code']}")

        for data_entry in data["return"]:
            class_entries.append(ClassEntry.from_data(data_entry))

        class_entries.sort(key=lambda entry: entry.start_time)

        return class_entries
