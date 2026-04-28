from app.bot.actions.base import BaseAction
from app.bot.enums.language import Language


class SwitchLanguageAction(BaseAction, prefix="switch_language"):
    language: Language
