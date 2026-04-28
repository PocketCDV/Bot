from starlette import status

from app.asgi.api.v1.exceptions import APIError


class InvalidTelegramInitDataError(APIError):
    """
    Raised when an invalid telegram init data is provided.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
