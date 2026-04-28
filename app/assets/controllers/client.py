from typing import Any, Dict

from aiohttp import ClientSession, ClientConnectorError, ServerConnectionError, ClientOSError

from app.assets.controllers.session import AbstractSessionController


class ClientController(AbstractSessionController[ClientSession]):
    """
    API Client session controller. Creates only one client session per instance,
    and yields it via async context manager.
    """

    def __init__(
            self,
            *,
            base_url: str | None = None,
            headers: Dict[str, Any] | None = None,
    ) -> None:
        """
        ClientController Constructor.
        :param base_url: Base URL of the client session.
        :param headers: Dictionary of headers.
        """

        super().__init__()
        self._base_url: str | None = base_url
        self._headers: dict | None = headers

    async def _create_session(self) -> ClientSession:
        return ClientSession(base_url=self._base_url, headers=self._headers)

    async def _validate_session(self) -> bool:
        return not self._session.closed

    async def _close_session(self) -> None:
        await self._session.close()

    def _is_recoverable_error(self, error: Exception) -> bool:
        return isinstance(error, (ClientConnectorError, ServerConnectionError, ClientOSError))
