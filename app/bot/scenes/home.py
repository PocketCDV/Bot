from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery

from app.assets.controllers.session import SessionController


class HomeScene(Scene, state="home", reset_data_on_enter=True):
    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            session_controller: SessionController,
    ) -> None:
        print(session_controller.get_session(callback_query.from_user.id))
