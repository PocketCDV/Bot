import asyncio
from http.cookies import Morsel
from ssl import create_default_context, SSLContext

from aiohttp import ClientSession, ClientTimeout, ClientConnectorCertificateError, ClientConnectionError
from certifi import where
from redis.asyncio import Redis
from starlette import status
from starlette.exceptions import HTTPException


class SessionController:
    """
    Stores WU session ID in Redis.
    """

    SSL_CONTEXT: SSLContext = create_default_context(cafile=where())

    def __init__(
            self,
            redis: Redis
    ) -> None:
        self._redis: Redis = redis

    async def get_session(
            self,
            telegram_id: int,
    ) -> str:
        """
        Retrieve session ID using user's Telegram ID.

        :param telegram_id: User's Telegram ID.

        :return: Session ID.
        """

        return await self._redis.get(self.key(telegram_id))

    async def set_session(
            self,
            telegram_id: int,
            session_id: str,
            expire: int | None = None,
    ) -> None:
        """
        Set new session ID using user's Telegram ID.

        :param telegram_id: User's Telegram ID.
        :param session_id: Session ID.
        :param expire: Expiration time, defaults to 30 minutes.

        :return:
        """

        await self._redis.set(self.key(telegram_id), session_id, ex=expire or 1800)

    @classmethod
    async def try_fetch_session(
            cls,
            login: str,
            password: str,
    ) -> str:
        try:
            async with ClientSession() as session:
                session_id: str = await cls._fetch_session(session, login, password)
                if session_id is None or not await cls._verify_session_id(session, session_id):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                    )
        except HTTPException:
            raise
        except ClientConnectorCertificateError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SSL error when connecting to WU server",
            )
        except ClientConnectionError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not reach WU server",
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Timed out",
            )

        return session_id

    async def try_refresh_session(
            self,
            telegram_id: int,
    ) -> None:
        pass

    @classmethod
    async def _fetch_session(
            cls,
            session: ClientSession,
            login: str,
            password: str,
    ) -> str | None:
        async with session.post(
                "https://wu.cdv.pl/?login=1",
                data={
                    "login": login,
                    "password": password,
                    "redirectUrl": "https://wu.cdv.pl?page=Main",
                },
                allow_redirects=False,
                ssl=cls.SSL_CONTEXT,
                timeout=ClientTimeout(total=10),
        ) as response:
            phpsessid: Morsel | None = response.cookies.get("WU_PHPSESSID")

        return phpsessid.value

    @classmethod
    async def _verify_session_id(
            cls,
            session: ClientSession,
            session_id: str,
    ) -> bool:
        async with session.get(
                "https://wu.cdv.pl/?page=Main",
                cookies={"WU_PHPSESSID": session_id},
                ssl=cls.SSL_CONTEXT,
        ) as response:
            return "?logout=1" in await response.text()

    @classmethod
    def key(
            cls,
            telegram_id: int,
    ) -> str:
        return f"pocketcdv:session:{telegram_id}"
