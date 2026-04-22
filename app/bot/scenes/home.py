from aiogram.fsm.scene import Scene, on
from aiogram.types import CallbackQuery, Message
from aiohttp import ClientSession

from app.assets.controllers.session import SessionController


class HomeScene(Scene, state="home", reset_data_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            session_controller: SessionController,
    ) -> None:
        session_id: str = await session_controller.get_session(message.from_user.id)

        async with ClientSession() as session:
            async with session.get(
                    "https://wu.cdv.pl/?page=Main",
                    cookies={"WU_PHPSESSID": session_id},
                    ssl=SessionController.SSL_CONTEXT,
            ) as response:
                print(await response.text())

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            session_controller: SessionController,
    ) -> None:
        session_id: str = await session_controller.get_session(callback_query.from_user.id)

        async with ClientSession() as session:
            async with session.get(
                    "https://wu.cdv.pl/?page=Main",
                    cookies={"WU_PHPSESSID": session_id},
                    ssl=SessionController.SSL_CONTEXT,
            ) as response:
                print(await response.text())
