import asyncio
from dataclasses import dataclass
from typing import Callable, Any, Awaitable, Set, Dict

from aiogram import BaseMiddleware, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup, Message


@dataclass
class UserMessage:
    user_id: int
    message_id: int | None

    _bot: Bot

    async def new_message(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        new_message, _ = await asyncio.gather(
            self._bot.send_message(
                chat_id=self.user_id,
                text=text,
                reply_markup=reply_markup,
            ),
            self._bot.delete_message(
                self.user_id,
                self.message_id
            ),
            return_exceptions=True,
        )

        self.message_id = new_message.message_id

    async def edit_message(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        try:
            if self.message_id is None:
                raise ValueError

            await self._bot.edit_message_text(
                chat_id=self.user_id,
                message_id=self.message_id,
                text=text,
                reply_markup=reply_markup,
            )
        except (TelegramBadRequest, ValueError):
            await self.new_message(
                text,
                reply_markup=reply_markup,
            )


class MessageIdMiddleware(BaseMiddleware):
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

        message_id: int = await state.get_value("message_id")
        user_message: UserMessage = UserMessage(
            from_user.id,
            message_id,
            _bot=data.get("bot")
        )

        data["user_message"] = user_message
        result: Any = await handler(event, data)

        if user_message.message_id != message_id:
            await state.update_data(message_id=user_message.message_id)

        return result
