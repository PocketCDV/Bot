from abc import ABC

from aiogram.filters.callback_data import CallbackData


class BaseAction(CallbackData, ABC, prefix="base"):
    """
    Base class for all callback actions.
    """
