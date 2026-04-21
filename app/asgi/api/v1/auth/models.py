from pydantic import BaseModel


class LoginModel(BaseModel):
    login: str
    password: str
    telegram_init_data: str
