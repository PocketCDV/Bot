from aiogram import Router
from aiogram.filters import Command

from app.bot.actions.home import HomeAction
from app.bot.scenes.home import HomeScene

home_router = Router(name=__name__)


home_router.message.register(
    HomeScene.as_handler(),
    Command("home"),
)


home_router.callback_query.register(
    HomeScene.as_handler(),
    HomeAction.filter()
)
