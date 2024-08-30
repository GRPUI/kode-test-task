from asyncpg import Connection
from fastapi import APIRouter, Depends

from deps import DatabaseConnectionMarker, SettingsMarker
from models.users import AddUserModel, UserTokenModel, RefreshTokenModel
from services import users

router = APIRouter()


@router.post("/signup")
async def signup(
    data: AddUserModel,
    connection: Connection = Depends(DatabaseConnectionMarker),
    settings: SettingsMarker = Depends(SettingsMarker),
) -> UserTokenModel:
    jwt_secret = settings.jwt_secret_key
    return await users.signup(data, connection, jwt_secret)


@router.post("/login")
async def signup(
    data: AddUserModel,
    connection: Connection = Depends(DatabaseConnectionMarker),
    settings: SettingsMarker = Depends(SettingsMarker),
) -> UserTokenModel:
    jwt_secret = settings.jwt_secret_key
    return await users.login(data, connection, jwt_secret)


@router.post("/renew")
async def renew(
    data: RefreshTokenModel,
    settings: SettingsMarker = Depends(SettingsMarker),
    connection: Connection = Depends(DatabaseConnectionMarker),
) -> UserTokenModel:
    jwt_secret = settings.jwt_secret_key
    return await users.renew(data, connection, jwt_secret)
