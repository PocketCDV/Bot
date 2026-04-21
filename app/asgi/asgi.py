from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import ValidationError
from redis.asyncio import Redis
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.asgi.api.router import api_router
from app.asgi.controllers.session import SessionController
from app.asgi.logging import logger
from config import config


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    redis = Redis.from_url(config.redis_dsn.get_secret_value())

    fastapi_app.state.config = config
    fastapi_app.state.session_controller = SessionController(redis)

    yield

    await redis.close()

app = FastAPI(title=config.TITLE, lifespan=lifespan)

app.include_router(api_router)


@app.exception_handler(ValidationError)
async def on_validation_error(
        request: Request,
        exception: ValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Executes when a Pydantic model provided by either user or ASGI is invalid.

    :param request: API request instance.
    :param exception: ValidationError instance.

    :return: JSON API response.
    """

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exception.errors()}
    )


@app.exception_handler(Exception)
async def on_server_error(
        request: Request,
        exception: Exception
) -> JSONResponse:
    """
    Handler for all errors.

    Executes when ASGI server raises any internal exception which should be inspected and debugged.

    :param request: API request instance.
    :param exception: Exception instance.

    :return: JSON API response.
    """

    logger.exception(exception)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
