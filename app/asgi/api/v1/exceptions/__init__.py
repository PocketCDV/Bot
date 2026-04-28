from starlette import status


class APIError(Exception):
    """
    Base error class for all API exceptions.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
