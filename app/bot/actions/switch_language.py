from app.bot.actions.base import BaseAction
from app.bot.enums.locale import Locale


class SwitchLanguageAction(BaseAction, prefix="switch_language"):
    locale: Locale
