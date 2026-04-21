import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.loggers import event
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.log import access_logger
from aiohttp.web_app import Application

from app.bot import create_dispatcher
from config import config


async def on_startup(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_webhook(
        config.webhook_url,
        secret_token=config.telegram_secret.get_secret_value(),
    )


def main() -> None:
    if config.telegram_secret is None:
        raise ValueError("Telegram secret is not set")
    if config.webhook_url is None:
        raise ValueError("Webhook URL is not set")
    if config.webhook_path is None:
        raise ValueError("Webhook path is not set")

    dispatcher: Dispatcher = create_dispatcher()
    dispatcher.startup.register(on_startup)

    bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    app = Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=config.telegram_secret.get_secret_value(),
    )
    webhook_requests_handler.register(app, path=config.webhook_path)
    setup_application(app, dispatcher, bot=bot)

    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
    )


if __name__ == "__main__":
    if sys.platform == "win32":  # Using SelectorEventLoop on Windows to avoid psycopg exceptions
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )

    access_logger.setLevel(logging.ERROR)
    event.setLevel(logging.ERROR)

    main()
