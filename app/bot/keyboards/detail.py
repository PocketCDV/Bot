from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from app.assets.models.class_record import ClassRecord
from app.bot.actions.back import BackAction


def get_detail_keyboard(
        class_record: ClassRecord,
        i18n: I18nContext,
) -> InlineKeyboardMarkup:
    """
    Inline keyboard for the detailed class info page.
    :param class_record: ClassRecord instance.
    :param i18n: I18n context.
    :return: InlineKeyboardMarkup.
    """

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if class_record.online_meeting_url is not None:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get(
                    "button-join-meeting",
                ),
                url=class_record.online_meeting_url,
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=i18n.get("button-back"),
            callback_data=BackAction().pack(),
        )
    )

    return builder.as_markup()
