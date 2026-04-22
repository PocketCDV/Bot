from redis.asyncio import Redis


# TODO: Replace with cached user controller
class MessageController:
    def __init__(
            self,
            redis: Redis,
    ) -> None:
        self._redis = redis

    async def get_message_id(
            self,
            telegram_id: int,
    ) -> int:
        return await self._redis.get(self.key(telegram_id))

    async def set_message_id(
            self,
            telegram_id: int,
            message_id: int,
    ) -> None:
        await self._redis.set(self.key(telegram_id), message_id)

    @classmethod
    def key(
            cls,
            telegram_id: int,
    ) -> str:
        return f"pocketcdv:message:{telegram_id}"
