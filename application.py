"""FastAPI application factory and lifecycle wiring."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from api.routes.chat import router as chat_router
from api.routes.document import router as document_router
from api.routes.health import router as health_router
from api.routes.ui import router as ui_router
from config import DeepAgentSettings, get_settings
from infrastructure.database.models import Base
from infrastructure.database.session import configure_session, init_engine


async def prepare_database(engine: AsyncEngine) -> None:
    """Create local tables required by the standalone service."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize infrastructure shared by the application."""
    settings = get_settings()
    engine = init_engine(settings.database_url)
    configure_session(engine)
    await prepare_database(engine)
    app.state.engine = engine
    yield
    await engine.dispose()


def create_app(settings: DeepAgentSettings | None = None) -> FastAPI:
    """Build the standalone agents application."""
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.debug,
        lifespan=lifespan,
    )
    # Router order keeps the composition root explicit: UI first, then API endpoints.
    app.include_router(ui_router)
    app.include_router(health_router, prefix=resolved_settings.api_prefix)
    app.include_router(chat_router, prefix=resolved_settings.api_prefix)
    app.include_router(document_router, prefix=resolved_settings.api_prefix)
    return app
