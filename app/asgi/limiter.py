from slowapi import Limiter
from slowapi.util import get_remote_address


# Main Limiter instance.
limiter: Limiter = Limiter(key_func=get_remote_address)
