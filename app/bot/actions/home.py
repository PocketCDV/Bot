from app.bot.actions import BaseAction


class HomeAction(BaseAction, prefix="home"):
    """
    Callback action for returning to the home page.
    """
