from pydantic import BaseModel


class AddUserModel(BaseModel):
    """
    Модель для создания пользователя

    Атрибуты:

    username: str -- имя пользователя;
    password: str -- пароль пользователя.
    """

    username: str
    password: str


class UserTokenModel(BaseModel):
    """
    Модель для токенов пользователя

    Атрибуты:

    access_token: str -- токен доступа;
    refresh_token: str -- токен обновления.
    """

    access_token: str
    refresh_token: str


class RefreshTokenModel(BaseModel):
    """
    Модель для обновления токена

    Атрибуты:

    refresh_token: str -- токен обновления.
    """

    refresh_token: str
