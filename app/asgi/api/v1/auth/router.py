import asyncio
from ssl import create_default_context
from typing import Annotated

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from aiohttp import ClientSession, ClientTimeout, ClientConnectorCertificateError, ClientConnectionError
from certifi import where
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.assets.controllers.session import SessionController
from app.asgi.dependencies import config_dependency, session_controller_dependency
from app.asgi.limiter import limiter
from config import Config

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("5/minute")
async def login(
        request: Request,
        login_model: LoginModel,
        config: Annotated[Config, Depends(config_dependency)],
        session_controller: Annotated[SessionController, Depends(session_controller_dependency)],
) -> None:
    try:
        telegram_init_data: WebAppInitData = safe_parse_webapp_init_data(
            token=config.telegram_bot_token.get_secret_value(),
            init_data=login_model.telegram_init_data,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    ssl_context = create_default_context(cafile=where())

    try:
        async with ClientSession() as session:
            async with session.post(
                "https://wu.cdv.pl/?login=1",
                data={
                    "login": login_model.login,
                    "password": login_model.password,
                    "redirectUrl": "https://wu.cdv.pl?page=Main",
                },
                allow_redirects=False,
                ssl=ssl_context,
                timeout=ClientTimeout(total=10),
            ) as response:
                phpsessid = response.cookies.get("WU_PHPSESSID")

                if phpsessid is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                    )

                session_id: str = phpsessid.value
    except HTTPException:
        raise
    except ClientConnectorCertificateError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SSL error when connecting to WU server",
        )
    except ClientConnectionError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not reach WU server",
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timed out",
        )

    await session_controller.set_session(telegram_init_data.user.id, session_id)
