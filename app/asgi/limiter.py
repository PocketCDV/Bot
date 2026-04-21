from slowapi import Limiter
from starlette.requests import Request


def get_ip(request: Request) -> str:
    """
    Returns the IP address of the client.
    """

    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host


# Main Limiter instance.
limiter: Limiter = Limiter(key_func=get_ip)
