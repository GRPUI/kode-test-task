from datetime import timedelta, datetime, timezone
from typing import Dict, Any
from uuid import uuid4

import jwt
from asyncpg import Connection
from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from jwt import InvalidTokenError

from deps import SettingsMarker
from models.users import UserTokenModel, AddUserModel, RefreshTokenModel


async def signup(
    data: AddUserModel, connection: Connection, jwt_secret: str
) -> UserTokenModel:
    """
    Функция для регистрации пользователя

    :param data:
    :param connection:
    :param jwt_secret:
    :return:
    """
    user = await connection.fetchrow(
        "SELECT id FROM users WHERE username = $1", data.username
    )
    if user:
        raise HTTPException(status_code=409, detail="User already exists")

    user_id = await connection.fetchval(
        "INSERT INTO users (username, password, created_at) "
        "VALUES ($1, $2, NOW()) "
        "RETURNING id",
        data.username,
        data.password,
    )

    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))
    refresh = await sign_token("refresh", user_id, jwt_secret, ttl=timedelta(days=30))

    return UserTokenModel(access_token=access, refresh_token=refresh)


async def login(
    data: AddUserModel, connection: Connection, jwt_secret: str
) -> UserTokenModel:
    """
    Функция для авторизации пользователя

    :param data:
    :param connection:
    :param jwt_secret:
    :return:
    """
    user = await connection.fetchrow(
        "SELECT id FROM users WHERE username = $1 AND password = $2",
        data.username,
        data.password,
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = user["id"]

    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))
    refresh = await sign_token("refresh", user_id, jwt_secret, ttl=timedelta(days=30))

    return UserTokenModel(access_token=access, refresh_token=refresh)


async def sign_token(
    jwt_type: str,
    subject: int,
    jwt_secret: str,
    payload: Dict[str, Any] = {},
    ttl: timedelta = None,
) -> str:
    """
    Функция для создания токена

    :param jwt_type:
    :param subject:
    :param jwt_secret:
    :param payload:
    :param ttl:
    :return:
    """
    current_timestamp = datetime.now(tz=timezone.utc).timestamp()

    data = dict(
        iss="kode@auth_service",
        sub=subject,
        type=jwt_type,
        jti=str(uuid4()),
        iat=current_timestamp,
        nbf=payload["nbf"] if payload.get("nbf") else current_timestamp,
    )
    data.update(dict(exp=data["nbf"] + int(ttl.total_seconds()))) if ttl else None
    payload.update(data)

    return jwt.encode(payload=payload, key=jwt_secret, algorithm="HS256")


async def check_access_token(
    authorization_header: str = Security(
        APIKeyHeader(name="Authorization", auto_error=False)
    ),
    settings: SettingsMarker = Depends(SettingsMarker),
) -> int:
    """
    Функция для проверки токена

    :param authorization_header:
    :param settings:
    :return:
    """
    if authorization_header is None:
        raise HTTPException(status_code=401, detail="Token is required")

    if "Bearer " not in authorization_header:
        raise HTTPException(status_code=401, detail="Invalid token")

    clear_token = authorization_header.replace("Bearer ", "")

    try:
        payload = jwt.decode(
            jwt=clear_token, key=settings.jwt_secret_key, algorithms=["HS256", "RS256"]
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id


async def renew(
    data: RefreshTokenModel, connection: Connection, jwt_secret: str
) -> UserTokenModel:
    """
    Функция для обновления токена

    :param connection:
    :param data:
    :param jwt_secret:
    :return:
    """
    user_id = jwt.decode(
        jwt=data.refresh_token, key=jwt_secret, algorithms=["HS256"]
    ).get("sub")

    exists = await connection.fetchrow("SELECT id FROM users WHERE id = $1", user_id)

    if not exists:
        raise HTTPException(status_code=401, detail="Invalid token")

    access = await sign_token("access", user_id, jwt_secret, ttl=timedelta(minutes=15))
    refresh = data.refresh_token

    return UserTokenModel(access_token=access, refresh_token=refresh)
