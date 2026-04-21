from aiogram.fsm.scene import Scene, on
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.utils.i18n import gettext as _

from app.bot.actions.proceed import ProceedAction


class StartScene(Scene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    """
    Base entry scene, introduction for new users and a home page for logged-in users.
    """

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
    ) -> None:
        await message.answer(
            _("message.greeting_1").format(first_name=message.from_user.first_name),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=_("button.proceed"), callback_data=ProceedAction().pack()),
                    ]
                ]
            )
        )
        await message.delete()

    @on.callback_query(ProceedAction.filter())
    async def on_proceed(
            self,
            callback_query: CallbackQuery,
    ) -> None:
        await callback_query.message.edit_text(
            _("message.greeting_2"),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("button.login_via_vc"),
                            web_app=WebAppInfo(url="https://github.com/PocketCDV")
                        )
                    ]
                ]
            )
        )
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
