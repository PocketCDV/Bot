import asyncio
from typing import Sequence, Coroutine, Any, List, Set, Tuple, Dict

from aiogram import Bot
from aiogram.fsm.scene import Scene, on
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assets.controllers.api import APIController
from app.assets.models.class_entry import ClassEntry
from app.bot.middlewares.message_id import UserMessage
from app.database.models import Room


class HomeScene(Scene, state="home"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            bot: Bot,
            database_session: AsyncSession,
            user_message: UserMessage,
            session_id: str,
            api_controller: APIController,
    ) -> None:
        await self._open_home_page(
            bot=bot,
            database_session=database_session,
            user_message=user_message,
            session_id=session_id,
            api_controller=api_controller,
            delete_message_id=message.message_id,
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            bot: Bot,
            database_session: AsyncSession,
            user_message: UserMessage,
            session_id: str,
            api_controller: APIController,
    ) -> None:
        await self._open_home_page(
            bot=bot,
            database_session=database_session,
            user_message=user_message,
            session_id=session_id,
            api_controller=api_controller,
        )

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()

    async def _open_home_page(
            self,
            bot: Bot,
            database_session: AsyncSession,
            user_message: UserMessage,
            session_id: str,
            api_controller: APIController,
            *,
            delete_message_id: int | None = None,
    ) -> None:
        if session_id is None:
            await self.wizard.goto("login")
            return

        class_entries: Sequence[ClassEntry] = await api_controller.get_upcoming_schedule(session_id)

        room_ids: Tuple[int] = tuple(dict.fromkeys(class_entry.room for class_entry in class_entries))
        result = await database_session.scalars(
            select(Room.name)
            .filter(Room.id.in_(room_ids))
        )
        room_names: Dict[int, str] = dict(zip(room_ids, result.all()))

        class_entries_strings: List[str] = []
        for class_entry in class_entries:
            class_entries_strings.append(
                _("message.schedule.class_entry.short").format(
                    title=class_entry.title,
                    start_time=class_entry.start_time.strftime("%H:%M"),
                    end_time=class_entry.end_time.strftime("%H:%M"),
                    room=room_names[class_entry.room],
                )
            )

        home_message_coroutine: Coroutine[Any, Any, None] = user_message.edit_message(
            _("message.home").format(
                classes="\n\n".join(class_entries_strings),
            )
        )

        if delete_message_id is not None:
            await asyncio.gather(
                home_message_coroutine,
                bot.delete_message(
                    user_message.user_id,
                    delete_message_id,
                ),
                return_exceptions=True,
            )
        else:
            await home_message_coroutine
