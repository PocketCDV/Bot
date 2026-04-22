from aiogram import Router

from app.bot.actions.home import HomeAction
from app.bot.scenes.home import HomeScene

home_router = Router(name=__name__)


home_router.callback_query.register(
    HomeScene.as_handler(),
    HomeAction.filter()
)
