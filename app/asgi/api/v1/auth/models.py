from pydantic import BaseModel


class LoginModel(BaseModel):
    """
    API Model for logging in via WU Credentials, with Telegram Init Data to validate.
    """

    login: str
    """
    User's WU login (Email).
    """

    password: str
    """
    User's WU password.
    """

    telegram_init_data: str
    """
    Telegram Init Data to validate.
    """
