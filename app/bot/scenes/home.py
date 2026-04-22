from datetime import datetime, timedelta
from typing import Sequence

from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery, Message

from app.assets.controllers.api import APIController
from app.assets.controllers.session import SessionController
from app.assets.models.class_entry import ClassEntry


class HomeScene(Scene, state="home", reset_data_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            api_controller: APIController,
    ) -> None:
        class_entries: Sequence[ClassEntry] = await api_controller.get_upcoming_schedule(message.from_user.id)

        s = ""
        for class_entry in class_entries:
            s += f"{class_entry.title}\n{class_entry.room}\n\n"

        await message.answer(s)

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            session_controller: SessionController,
    ) -> None:
        pass
