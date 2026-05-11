from enum import StrEnum


class NotificationKind(StrEnum):
    """
    Enum of notification kinds that can be toggled in user settings.
    """

    UPCOMING = "upcoming"
    DAILY = "daily"
