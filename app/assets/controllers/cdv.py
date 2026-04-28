from datetime import date
from ssl import SSLContext
from typing import Any, Dict, List, Sequence

from aiohttp import ClientTimeout

from app.assets.controllers.client import ClientController
from app.assets.models.class_entry import ClassEntry
from app.bot.exceptions import BotError
from app.bot.exceptions.invalid_session import InvalidSessionError


class CDVController:
    """
    An abstraction above ClientController for interacting with WU API.
    """

    def __init__(
            self,
            client: ClientController,
            *,
            ssl_context: SSLContext | None = None,
    ) -> None:
        """
        CDVController Constructor.
        :param client: ClientController instance.
        :param ssl_context: SSLContext.
        """

        self._client: ClientController = client
        self._ssl_context: SSLContext | None = ssl_context

    async def get_session_id(
            self,
            login: str,
            password: str,
    ) -> str | None:
        """
        Retrieves WU session ID using credentials. Must be validated using refresh method.
        :param login: WU login (Email).
        :param password: WU password.
        :return: WU session ID.
        """

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
                cookie = response.cookies.get("WU_PHPSESSID")
                return cookie.value if cookie else None

    async def refresh_session_id(
            self,
            session_id: str,
    ) -> str | None:
        """
        Refreshes WU session ID and returns it. If session ID is invalid, returns None.
        :param session_id: WU session ID to refresh.
        :return: Refreshed session ID.
        """

        async with self._client.session() as client_session:
            async with client_session.get(
                f"/ajax.php",
                params={"action": "get-translations"},
                cookies={"WU_PHPSESSID": session_id},
                ssl=self._ssl_context,
            ) as response:
                try:
                    if response.status == 200 and not int((await response.json())["error_code"]):
                        cookie = response.cookies.get("WU_PHPSESSID")
                        return cookie.value if cookie else None
                    else:
                        return None
                except (TypeError, ValueError):
                    return None

    async def get_schedule(
            self,
            session_id: str,
            start_date: date,
            end_date: date,
    ) -> Sequence[ClassEntry]:
        """
        Retrieves all user's class entries as a sorted sequence using WU session ID.
        :param session_id: WU session ID.
        :param start_date: Start date of all class entries.
        :param end_date: End date of all class entries.
        :return: Sequence of class entries.
        :raises InvalidSessionError: If session ID is invalid.
        """

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
