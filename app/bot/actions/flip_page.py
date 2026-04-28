from app.bot.actions import BaseAction


class FlipPageAction(BaseAction, prefix="flip_page"):
    """
    Callback action for flipping a page on a paginated scene.
    """

    offset: int
    """
    Flip offset.
    """

    @classmethod
    def forwards(cls) -> 'FlipPageAction': return FlipPageAction(offset=1)

    @classmethod
    def backwards(cls) -> 'FlipPageAction': return FlipPageAction(offset=-1)
