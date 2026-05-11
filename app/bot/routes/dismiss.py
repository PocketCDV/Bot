from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from app.bot.actions.dismiss import DismissAction

dismiss_router = Router(name=__name__)


@dismiss_router.callback_query(DismissAction.filter())
async def dismiss(callback: CallbackQuery, bot: Bot) -> None:
    """
    Delete the message that owns the dismiss button. No state changes,
    no fetches — purely local.
    """

    try:
        await bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
        )
    except TelegramBadRequest:
        pass

    await callback.answer()
