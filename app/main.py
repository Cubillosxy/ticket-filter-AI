from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name)
    app.include_router(router)
    return app


_app = create_app()


app = _app
