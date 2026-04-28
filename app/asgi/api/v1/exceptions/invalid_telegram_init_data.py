from starlette import status

from app.asgi.api.v1.exceptions import APIError


class InvalidTelegramInitDataError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
