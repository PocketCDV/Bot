from starlette import status

from app.asgi.api.v1.exceptions import APIError


class InvalidCredentialsError(APIError):
    """
    Raised when invalid credentials are provided.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
