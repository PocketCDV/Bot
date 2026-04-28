from abc import ABC, abstractmethod
from asyncio import Lock
from contextlib import asynccontextmanager
from typing import TypeVar, Generic, AsyncIterator

_S = TypeVar("_S")


class AbstractSessionController(Generic[_S], ABC):
    def __init__(self) -> None:
        self._session: _S | None = None
        self._lock: Lock = Lock()

    @abstractmethod
    async def _create_session(self) -> _S:
        """
        Create a new session instance.
        """

    @abstractmethod
    async def _validate_session(self) -> bool:
        """
        Return True if session is still usable.
        """

    @abstractmethod
    async def _close_session(self) -> None:
        """
        Gracefully close the session.
        """

    @abstractmethod
    def _is_recoverable_error(self, error: Exception) -> bool:
        """
        Return True if error means session should be recreated.
        """

    @asynccontextmanager
    async def session(self) -> AsyncIterator[_S]:
        session: _S = await self._ensure_session()
        try:
            yield session
        except Exception as exc:
            if self._is_recoverable_error(exc):
                await self._invalidate()
            raise

    async def _ensure_session(self) -> _S:
        if self._session is not None and await self._validate_session():
            return self._session

        async with self._lock:
            if self._session is not None and await self._validate_session():
                return self._session

            if self._session is not None:
                try:
                    await self._close_session()
                except Exception:  # noqa
                    pass

            self._session: _S = await self._create_session()
            return self._session

    async def _invalidate(self) -> None:
        async with self._lock:
            if self._session is not None:
                try:
                    await self._close_session()
                except Exception:  # noqa
                    pass
                self._session = None
