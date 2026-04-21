from redis.asyncio import Redis


class SessionController:
    """
    Stores WU session ID in Redis.
    """

    def __init__(
            self,
            redis: Redis
    ) -> None:
        self._redis: Redis = redis

    async def set_session(
            self,
            telegram_id: int,
            session_id: str,
            expire: int = 1800,
    ) -> None:
        await self._redis.set(self.key(telegram_id), session_id, ex=expire)

    async def get_session(
            self,
            telegram_id: int,
    ) -> str:
        return await self._redis.get(self.key(telegram_id))

    @classmethod
    def key(
            cls,
            telegram_id: int,
    ) -> str:
        return f"pocketcdv:session:{telegram_id}"
