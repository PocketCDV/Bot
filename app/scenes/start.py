from aiogram.fsm.scene import Scene, on
from aiogram.types import Message
from aiogram.utils.i18n import gettext as _


class StartScene(Scene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
    ) -> None:
        await message.reply(_("message.start").format(first_name=message.from_user.first_name))

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
