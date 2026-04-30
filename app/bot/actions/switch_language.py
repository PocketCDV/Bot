from app.bot.actions import BaseAction
from app.assets.enums.language import Language


class SwitchLanguageAction(BaseAction, prefix="switch_language"):
    """
    Callback action for switching a language.
    """

    language: Language
    """
    New chosen language.
    """
