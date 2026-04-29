from aiogram import Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.payload import decode_payload
from aiogram_i18n import I18nContext

from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.enums.payload_action import PayloadAction
from app.bot.exceptions.invalid_session import InvalidSessionError
from app.bot.keyboards.home import get_home_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class HomeScene(BaseScene, state="home"):
    """
    Home page scene. Displays today's classes, updates every 10 minutes.
    """

    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user_message: UserMessage,
            session_id: str,
            bot: Bot,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            text, keyboard = await self._get_schedule_content(
                message.from_user.first_name,
                session_id,
                bot,
                i18n,
                schedule_controller,
            )
        except InvalidSessionError:
            await user_message.new_login(i18n)
            await self.wizard.exit()
            return

        await user_message.new(
            text,
            reply_markup=keyboard,
            message_to_delete=message.message_id,
        )

        logger.info(
            f"User {message.from_user.id} opened the home page."
        )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            session_id: str,
            bot: Bot,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        try:
            if session_id is None:
                raise InvalidSessionError

            text, keyboard = await self._get_schedule_content(
                callback_query.from_user.first_name,
                session_id,
                bot,
                i18n,
                schedule_controller,
            )
        except InvalidSessionError:
            await user_message.edit_login(i18n)
            await self.wizard.exit()
            return

        await user_message.edit(
            text,
            reply_markup=keyboard,
        )
        await callback_query.answer()

        logger.info(
            f"User {callback_query.from_user.id} opened the home page."
        )

    @on.message(CommandStart(deep_link=True))
    async def on_start(
            self,
            message: Message,
            command: CommandObject,
    ) -> None:
        await message.delete()

        payload: str = decode_payload(command.args)
        action, data = payload.split(":")

        if action != PayloadAction.DETAIL:
            return

        term_id: int = int(data)
        print(term_id)

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()

    @staticmethod
    async def _get_schedule_content(
            first_name: str,
            session_id: str,
            bot: Bot,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> tuple[str, InlineKeyboardMarkup]:
        """
        Retrieve message text as string, and a reply markup.
        :param first_name: User's first name.
        :param session_id: WU session ID.
        :param bot: Bot instance.
        :param i18n: I18n context.
        :param schedule_controller: ScheduleController instance.
        :return: Message text and a reply markup.
        """

        schedule: ScheduleDayRecord = await schedule_controller.get_home_schedule(session_id)

        if schedule.class_records:
            text: str = i18n.get("home", first_name=first_name, classes=await schedule.to_string(bot, i18n))
        else:
            text: str = i18n.get("home-no-classes", first_name=first_name)

        return text, get_home_keyboard(schedule, i18n)
