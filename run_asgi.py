import sys
from asyncio import SelectorEventLoop

import uvicorn.loops.asyncio

from app.asgi.logger import API_LOG_CONFIG

if __name__ == "__main__":
    if sys.platform == "win32":
        uvicorn.loops.asyncio.asyncio_loop_factory = lambda use_subprocess=False: SelectorEventLoop

    uvicorn.run(
        "app.asgi.asgi:app",
        host="0.0.0.0",
        port=8000,
        loop="asyncio",
        log_config=API_LOG_CONFIG,
    )
