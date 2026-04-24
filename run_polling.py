import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.loggers import event

from app.bot.bot import create_dispatcher
from config import config


async def main() -> None:
    dispatcher: Dispatcher = create_dispatcher()

    bot: Bot = Bot(
        token=config.telegram_bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(asctime)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )
    event.setLevel(logging.ERROR)

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    else:
        asyncio.run(main())
