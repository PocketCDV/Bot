import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Any, Awaitable, Dict, Coroutine, List

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject, User, InlineKeyboardMarkup, Message, LinkPreviewOptions
from aiogram_i18n import I18nContext

from app.assets.models.records.daily_schedule_record import DailyScheduleRecord
from app.bot.keyboards.home import get_home_keyboard
from app.bot.keyboards.login import get_login_keyboard
from app.utils import now_local


@dataclass
class UserMessage:
    """
    Dataclass which represents a bot's message with which user is working.
    Can be edited and replaced, and should be used instead of plain message.edit_text().
    """

    user_id: int
    """
    User's telegram ID.
    """

    message_id: int | None
    """
    Message ID.
    """

    _bot: Bot
    """
    Bot instance for executing methods using instance attributes.
    """

    async def new(
            self,
            text: str,
            *,
            reply_markup: InlineKeyboardMarkup | None = None,
            message_to_delete: int | None = None,
    ) -> None:
        """
        Replace a message with a new one.
        :param text: Text of the message.
        :param reply_markup: Reply markup.
        :param message_to_delete: Message ID which should be deleted alongside with an old message,
        usually a user's command.
        """

        coroutines: List[Coroutine] = [
            self._bot.send_message(
                chat_id=self.user_id,
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
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
        """
        Edit a message. Replaces old one if fails.
        :param text: Text of the message.
        :param reply_markup: Reply markup.
        :param message_to_delete: Message ID which should be deleted alongside with an old message,
        if editing fails.
        """

        try:
            if self.message_id is None:
                raise ValueError

            coroutines: List[Coroutine] = [
                self._bot.edit_message_text(
                    chat_id=self.user_id,
                    message_id=self.message_id,
                    text=text,
                    reply_markup=reply_markup,
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                ),
            ]

            if message_to_delete is not None:
                coroutines.append(
                    self._bot.delete_message(
                        self.user_id,
                        message_to_delete,
                    ),
                )

            result, *_ = await asyncio.gather(*coroutines, return_exceptions=True)

            if isinstance(result, Exception):
                raise result
        except (TelegramBadRequest, ValueError) as error:
            if isinstance(error, TelegramBadRequest) and "message is not modified" in error.message:
                return

            await self.new(
                text,
                reply_markup=reply_markup,
                message_to_delete=message_to_delete,
            )

    async def refresh_home_page(
            self,
            user: User,
            daily_schedule: DailyScheduleRecord,
            i18n: I18nContext,
    ) -> None:
        time: datetime = now_local()

        if daily_schedule.class_records:
            await self.edit(
                i18n.get(
                    "home-updated",
                    first_name=user.first_name,
                    classes=await daily_schedule.to_string(self._bot, i18n),
                    updated=time.strftime("%H:%M"),
                ),
                reply_markup=get_home_keyboard(daily_schedule, i18n),
            )
        else:
            await self.edit(
                i18n.get(
                    "home-no-classes-updated",
                    first_name=user.first_name,
                    updated=time.strftime("%H:%M"),
                ),
                reply_markup=get_home_keyboard(daily_schedule, i18n),
            )

    async def ask_to_log_in(
            self,
            i18n: I18nContext,
            *,
            message_to_delete: int | None = None,
    ) -> None:
        """
        New message which says that user should log in.
        :param i18n: I18n context.
        :param message_to_delete: Message ID which should be deleted alongside with an old message.
        """

        await self.edit(
            i18n.get("login"),
            reply_markup=get_login_keyboard(i18n),
            message_to_delete=message_to_delete,
        )


class UserMessageMiddleware(BaseMiddleware):
    """
    Middleware which provides a UserMessage object on each user-related event.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Inserts UserMessage object in workflow data, and updates it after handler execution.
        """

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
