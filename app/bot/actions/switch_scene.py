from app.bot.actions import BaseAction


class SwitchSceneAction(BaseAction, prefix="switch"):
    """
    Callback action for proceeding to a new scene.
    """

    scene: str
    """
    Chosen scene state.
    """
