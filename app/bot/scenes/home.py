from aiogram.fsm.scene import on
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_i18n import I18nContext

from app.assets.controllers.schedule import ScheduleController
from app.assets.models.schedule_day_record import ScheduleDayRecord
from app.bot.actions.switch_scene import SwitchSceneAction
from app.bot.middlewares.message_id import UserMessage
from app.bot.scenes.base import BaseScene


class HomeScene(BaseScene, state="home"):
    @on.message.enter()
    async def on_message_enter(
            self,
            message: Message,
            user_message: UserMessage,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        if session_id is None:
            await self.wizard.goto("login")
            return

        schedule: ScheduleDayRecord = await schedule_controller.get_home_schedule(session_id)

        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-view-schedule"),
                        callback_data=SwitchSceneAction(scene="schedule").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-lang"),
                        callback_data=SwitchSceneAction(scene="language").pack(),
                    )
                ],
            ]
        )

        if schedule.class_records:
            await user_message.new_message(
                i18n.get(
                    "home",
                    first_name=message.from_user.first_name,
                    classes=schedule.to_string(i18n),
                ),
                reply_markup=reply_markup,
                message_to_delete=message.message_id,
            )
        else:
            await user_message.new_message(
                i18n.get(
                    "home-no-classes",
                    first_name=message.from_user.first_name,
                ),
                reply_markup=reply_markup,
                message_to_delete=message.message_id,
            )

    @on.callback_query.enter()
    async def on_callback_query_enter(
            self,
            callback_query: CallbackQuery,
            user_message: UserMessage,
            session_id: str,
            i18n: I18nContext,
            schedule_controller: ScheduleController,
    ) -> None:
        if session_id is None:
            await self.wizard.goto("login")
            return

        schedule: ScheduleDayRecord = await schedule_controller.get_home_schedule(session_id)

        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-view-schedule"),
                        callback_data=SwitchSceneAction(scene="schedule").pack(),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=i18n.get("button-lang"),
                        callback_data=SwitchSceneAction(scene="language").pack(),
                    )
                ],
            ]
        )

        if schedule.class_records:
            await user_message.edit_message(
                i18n.get(
                    "home",
                    first_name=callback_query.from_user.first_name,
                    classes=schedule.to_string(i18n),
                ),
                reply_markup=reply_markup,
            )
        else:
            await user_message.edit_message(
                i18n.get(
                    "home-no-classes",
                    first_name=callback_query.from_user.first_name,
                ),
                reply_markup=reply_markup,
            )

        await callback_query.answer()

    @on.message()
    async def on_message(
            self,
            message: Message,
    ) -> None:
        await message.delete()
