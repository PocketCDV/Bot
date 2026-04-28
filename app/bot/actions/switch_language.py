from app.bot.actions import BaseAction
from app.bot.enums.language import Language


class SwitchLanguageAction(BaseAction, prefix="switch_language"):
    """
    Callback action for switching a language.
    """

    language: Language
    """
    New chosen language.
    """
