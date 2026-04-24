from app.bot.actions.base import BaseAction


class SwitchSceneAction(BaseAction, prefix="switch"):
    scene: str
