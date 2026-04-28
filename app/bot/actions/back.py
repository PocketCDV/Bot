from app.bot.actions import BaseAction


class BackAction(BaseAction, prefix="back"):
    """
    Callback action for returning to the previous scene.
    """
