from starlette import status

from app.asgi.api.v1.exceptions.api import APIError


class InvalidCredentialsError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
