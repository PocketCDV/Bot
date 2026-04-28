from typing import Self

from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine

from app.assets.controllers.session import AbstractSessionController


class DatabaseController(AbstractSessionController[AsyncSession]):
    """
    Database session controller. Creates only one session per instance,
    and yields it via async context manager.
    """

    def __init__(
            self,
            *,
            engine: AsyncEngine,
            session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        """
        DatabaseController Constructor.
        :param engine: SQLAlchemy database engine.
        :param session_maker: SQLAlchemy session maker.
        """

        super().__init__()
        self._engine: AsyncEngine = engine
        self._session_maker: async_sessionmaker[AsyncSession] = session_maker

    async def _create_session(self) -> AsyncSession:
        return self._session_maker()

    async def _validate_session(self) -> bool:
        return self._session.is_active

    async def _close_session(self) -> None:
        await self._session.close()

    def _is_recoverable_error(self, error: Exception) -> bool:
        return isinstance(error, (OperationalError, DisconnectionError))

    @classmethod
    def from_dsn(
            cls,
            dsn: str
    ) -> Self:
        """
        Creates DatabaseController instance from DSN string.
        :param dsn: Database DSN string.
        :return: DatabaseController instance.
        """

        engine: AsyncEngine = create_async_engine(
            dsn,
            pool_size=10,
            max_overflow=10,
            pool_recycle=60,
            pool_timeout=10
        )

        session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            engine,
            expire_on_commit=False,
            autocommit=False,
        )

        return cls(
            engine=engine,
            session_maker=session_maker,
        )
