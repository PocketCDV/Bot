from typing import ClassVar

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Provides credentials for all services, telegram bot token and webhook data, etc.
    """

    TITLE: ClassVar[str] = "PocketCDV"

    database_dsn: SecretStr
    """
    DSN for database connection.
    """

    redis_dsn: SecretStr
    """
    DSN for Redis connection.
    """

    rabbitmq_dsn: SecretStr
    """
    DSN for RabbitMQ connection.
    """

    result_backend_dsn: str = "rpc://"
    """
    DSN for retrieving task results.
    """

    telegram_bot_token: SecretStr
    """
    Telegram bot token.
    """

    telegram_secret: SecretStr | None = None
    """
    Telegram bot secret used to authenticating Telegram webhook (Required only if webhook is used).
    """

    webhook_url: str | None = None
    """
    Base webhook URL by which telegram will send updates (Required only if webhook is used).
    """

    webhook_path: str | None = None
    """
    URL path by which telegram will send updates (Required only if webhook is used).
    """

    api_url: str
    """
    CDV API URL.
    """

    web_app_url: str
    """
    URL for Telegram login web app.
    """

    log_level: int = 40
    """
    Application logging level. 10 for debug, 20 for info, 30 for warnings, 40 for errors.
    """


# Main Config instance.
config = Config(_env_file=".env")
