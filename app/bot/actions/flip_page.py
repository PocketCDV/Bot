from app.bot.actions.base import BaseAction


class FlipPageAction(BaseAction, prefix="flip_page"):
    offset: int

    @classmethod
    def forwards(cls) -> 'FlipPageAction': return FlipPageAction(offset=1)

    @classmethod
    def backwards(cls) -> 'FlipPageAction': return FlipPageAction(offset=-1)
