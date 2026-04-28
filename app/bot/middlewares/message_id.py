import asyncio
from dataclasses import dataclass
from typing import Callable, Any, Awaitable, Dict, Coroutine, List

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup, Message
from aiogram_i18n import I18nContext

from app.bot.keyboards.login import get_login_keyboard


@dataclass
class UserMessage:
    user_id: int
    message_id: int | None

    _bot: Bot

    async def new(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
            message_to_delete: int | None = None,
    ) -> None:
        coroutines: List[Coroutine] = [
            self._bot.send_message(
                chat_id=self.user_id,
                text=text,
                reply_markup=reply_markup,
            ),
            self._bot.delete_message(
                self.user_id,
                self.message_id
            ),
        ]

        if message_to_delete is not None:
            coroutines.append(
                self._bot.delete_message(
                    self.user_id,
                    message_to_delete
                )
            )

        new_message, *_ = await asyncio.gather(*coroutines, return_exceptions=True)

        if not isinstance(new_message, Message):
            return

        self.message_id = new_message.message_id

    async def edit(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
            message_to_delete: int | None = None,
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
        except (TelegramBadRequest, ValueError) as error:
            if isinstance(error, TelegramBadRequest) and "message is not modified" in error.message:
                return

            await self.new(
                text,
                reply_markup=reply_markup,
                message_to_delete=message_to_delete,
            )

    async def new_login(
            self,
            i18n: I18nContext,
            *,
            message_to_delete: int | None = None,
    ) -> None:
        await self.new(
            i18n.get("login"),
            reply_markup=get_login_keyboard(i18n),
            message_to_delete=message_to_delete,
        )

    async def edit_login(
            self,
            i18n: I18nContext,
    ) -> None:
        await self.edit(
            i18n.get("login"),
            reply_markup=get_login_keyboard(i18n),
        )


class MessageIdMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
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
