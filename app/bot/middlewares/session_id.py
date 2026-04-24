from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User

from app.assets.controllers.api import APIController


class SessionIDMiddleware(BaseMiddleware):
    def __init__(
            self,
            *,
            api_controller: APIController,
    ) -> None:
        self._api_controller = api_controller

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        from_user: User | None = data.get("event_from_user")

        if from_user is None:
            return await handler(event, data)

        state: FSMContext = data.get("state")
        session_id: str | None = await state.get_value("session_id")

        if session_id is None or (await self._api_controller.refresh_session_id(session_id)) is None:
            await state.update_data(session_id=None)
            data["session_id"] = None
        else:
            data["session_id"] = session_id

        return await handler(event, data)
