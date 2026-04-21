from aiogram import Router
from aiogram.filters import CommandStart

from app.bot.scenes.start import StartScene

start_router = Router(name=__name__)


start_router.message.register(
    StartScene.as_handler(),
    CommandStart(),
)
