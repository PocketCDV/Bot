from datetime import date
from ssl import SSLContext
from typing import Any, Dict, List, Sequence

from aiohttp import ClientTimeout

from app.assets.controllers.client import ClientController
from app.assets.models.class_entry import ClassEntry
from app.bot.exceptions import BotError
from app.bot.exceptions.invalid_session import InvalidSessionError


class CDVController:
    def __init__(
            self,
            client: ClientController,
            *,
            ssl_context: SSLContext | None = None,
    ) -> None:
        self._client: ClientController = client
        self._ssl_context: SSLContext | None = ssl_context

    async def get_session_id(
            self,
            login: str,
            password: str,
    ) -> str | None:
        async with self._client.session() as client_session:
            async with client_session.post(
                "/?login=1",
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
        async with self._client.session() as client_session:
            async with client_session.get(
                f"/ajax.php",
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

        async with self._client.session() as client_session:
            async with client_session.post(
                f"/ajax.php",
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
            if data["error_code"] == 56:
                raise InvalidSessionError("User session is invalid")
            raise BotError("An error occurred while retrieving schedule data")

        for data_entry in data["return"]:
            class_entries.append(ClassEntry.from_data(data_entry))

        class_entries.sort(key=lambda entry: entry.start_time)

        return class_entries
