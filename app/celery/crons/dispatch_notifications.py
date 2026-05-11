import asyncio
import sys
from typing import List, Tuple

from sqlalchemy import select

from app.assets.controllers.database import DatabaseController
from app.assets.enums.notification_kind import NotificationKind
from app.assets.models.database import Notification, User, UserSettings
from app.celery.tasks.send_daily_class_notification import send_daily_class_notification
from app.celery.tasks.send_upcoming_class_notification import send_upcoming_class_notification
from app.celery.worker import worker, config
from app.utils import now_local


async def __async_dispatch_notifications() -> None:
    """
    Asynchronously pick up due notifications, delete them from the database,
    and enqueue a Celery task for each one.
    """

    database: DatabaseController = DatabaseController.from_dsn(
        config.database_dsn.get_secret_value(),
    )

    async with database.session() as session:
        result = await session.execute(
            select(Notification, UserSettings.locale)
            .join(User, User.id == Notification.user_id)
            .join(UserSettings, UserSettings.user_id == User.id)
            .where(Notification.scheduled_at <= now_local())
        )
        due: List[Tuple[Notification, str | None]] = list(result.all())

        for notification, _ in due:
            await session.delete(notification)

        await session.commit()

    for notification, locale in due:
        if notification.kind == NotificationKind.DAILY:
            send_daily_class_notification.delay(
                telegram_id=notification.telegram_id,
                locale=locale,
                data=notification.data,
            )
        else:
            send_upcoming_class_notification.delay(
                telegram_id=notification.telegram_id,
                locale=locale,
                data=notification.data,
            )


@worker.task(name="dispatch_notifications")
def dispatch_notifications() -> None:
    """
    Celery task for dispatching all notifications which are due to be sent.
    """

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(__async_dispatch_notifications())
    else:
        asyncio.run(__async_dispatch_notifications())
