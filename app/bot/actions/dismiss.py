from app.bot.actions import BaseAction


class DismissAction(BaseAction, prefix="dismiss"):
    """
    Callback action for dismissing (deleting) a notification message.
    """
