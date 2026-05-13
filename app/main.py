from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, DB_PATH
from .routes import router


def create_app(db_path: Path = DB_PATH) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(app.state.db_path)
        yield

    app = FastAPI(
        title="Todo API",
        description="A clean REST API for managing tasks.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.state.db_path = db_path  # Injected path accessible from routes

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


app = create_app()
