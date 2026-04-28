from starlette import status

from app.asgi.api.v1.exceptions.api import APIError


class ServerUnavailableError(APIError):
    status_code = status.HTTP_502_BAD_GATEWAY
