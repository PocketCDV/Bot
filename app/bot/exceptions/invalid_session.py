from app.bot.exceptions import BotError


class InvalidSessionError(BotError):
    """
    Raised when bot tries to perform an action using invalid session.
    Means that user must log in again via WU Credentials to continue using bot's features.
    """
