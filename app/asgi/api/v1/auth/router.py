from typing import Annotated

from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from starlette import status
from starlette.requests import Request

from app.asgi.api.v1.auth.models import LoginModel
from app.asgi.dependencies import config_dependency, session_controller_dependency
from app.asgi.limiter import limiter
from app.assets.controllers.session import SessionController
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
        background_tasks: BackgroundTasks,
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

    session_id: str = await session_controller.try_fetch_session(
        login_model.login,
        login_model.password,
    )

    background_tasks.add_task(
        session_controller.set_session,
        telegram_id=telegram_init_data.user.id,
        session_id=session_id,
        expire=None,
    )
