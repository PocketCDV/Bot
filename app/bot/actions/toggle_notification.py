from app.assets.enums.notification_kind import NotificationKind
from app.bot.actions import BaseAction


class ToggleNotificationAction(BaseAction, prefix="toggle_notification"):
    """
    Callback action for toggling a notification preference.
    """

    kind: NotificationKind
    """
    Notification kind to toggle.
    """
