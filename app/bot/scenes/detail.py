from aiogram.fsm.scene import on
from aiogram.types import Message
from aiogram_i18n import I18nContext

from app.assets.models.class_record import ClassRecord
from app.bot.keyboards.detail import get_detail_keyboard
from app.bot.logger import logger
from app.bot.middlewares.user_message import UserMessage
from app.bot.scenes.base import BaseScene


class DetailScene(BaseScene, state="detail"):
    @on.message.enter()
    async def on_enter(
            self,
            message: Message,
            class_record: ClassRecord,
            user_message: UserMessage,
            i18n: I18nContext,
    ) -> None:
        await user_message.edit(
            i18n.get(
                "schedule-class-entry.detailed",
                title=class_record.title,
                module=class_record.module,
                form=class_record.form,
                date=class_record.start_time.strftime("%d.%m.%Y"),
                start_time=class_record.start_time.strftime("%H:%M"),
                end_time=class_record.end_time.strftime("%H:%M"),
                room=class_record.room_name,
                teacher=class_record.teacher_name,
            ),
            reply_markup=get_detail_keyboard(class_record, i18n),
            message_to_delete=message.message_id,
        )

        logger.info(
            f"User {message.from_user.id} opened details about class"
        )
