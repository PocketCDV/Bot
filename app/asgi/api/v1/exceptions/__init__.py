from starlette import status


class APIError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
