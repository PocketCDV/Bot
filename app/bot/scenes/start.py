from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from aiogram.utils.i18n import gettext as _

from app.bot.actions.home import HomeAction
from app.bot.actions.proceed import ProceedAction


class StartScene(Scene, state="start", reset_data_on_enter=True, reset_history_on_enter=True):
    """
    Base entry scene, introduction for new users and a home page for logged-in users.
    """

    @on.message.enter()
    async def on_enter(
            self,
            message: Message,
            state: FSMContext,
    ) -> None:
        new_message: Message = await message.answer(
            _("message.greeting_1").format(first_name=message.from_user.first_name),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=_("button.proceed"), callback_data=ProceedAction().pack())
                    ]
                ]
            )
        )
        await message.delete()

        await state.update_data(message_id=new_message.message_id)

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
                            web_app=WebAppInfo(url="https://card-sentence-cats-cook.trycloudflare.com"),
                        )
                    ]
                ]
            )
        )
        await callback_query.answer()

    @on.message(F.web_app_data.data == "successful_login")
    async def on_successful_login(
            self,
            message: Message,
            state: FSMContext,
    ) -> None:
        message_id: int = await state.get_value("message_id")

        await message.bot.edit_message_text(
            _("message.greeting.successful_login"),
            chat_id=message.chat.id,
            message_id=message_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=_("button.go_to_home"), callback_data=HomeAction().pack())
                    ]
                ]
            )
        )

    @on.callback_query(HomeAction.filter())
    async def on_go_to_home(
            self,
            callback_query: CallbackQuery,
    ) -> None:
        await self.wizard.goto("home")
        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
