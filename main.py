import asyncio
import os
from contextlib import asynccontextmanager

import asyncpg
import dotenv
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deps import DatabaseConnectionMarker, SettingsMarker
from routers import notes, users
from settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.dependency_overrides[SettingsMarker]()

    connection = await asyncpg.connect(
        f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"
    )

    app.dependency_overrides.update(
        {
            DatabaseConnectionMarker: lambda: connection,
        }
    )

    yield

    await connection.close()


def register_app(settings: Settings) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.dependency_overrides.update({SettingsMarker: lambda: settings})

    app.include_router(notes.router, prefix="/notes")
    app.include_router(users.router, prefix="/users")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )

    return app


def main():
    dotenv.load_dotenv()

    settings = Settings(
        db_name=os.getenv(key="DB_NAME"),
        db_host=os.getenv(key="DB_HOST"),
        db_user=os.getenv(key="DB_USER"),
        db_password=os.getenv(key="DB_PASSWORD"),
        cors_allowed_origins=os.getenv("ALLOWED_ORIGINS").split(","),
        cors_allowed_methods=os.getenv("ALLOWED_METHODS").split(","),
        cors_allowed_headers=os.getenv("ALLOWED_HEADERS").split(","),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
    )

    app = register_app(settings=settings)

    config = uvicorn.Config(app, host="0.0.0.0", port=8000)

    server = uvicorn.Server(config)

    asyncio.run(server.serve())


if __name__ == "__main__":
    main()
