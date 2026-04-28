from starlette import status

from app.asgi.api.v1.exceptions import APIError


class ServerUnavailableError(APIError):
    """
    Raised when a WU Server is unavailable.
    """

    status_code = status.HTTP_502_BAD_GATEWAY
