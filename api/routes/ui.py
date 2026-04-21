"""UI routes and static inline assets for manual debugging."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

from api.ui_assets import INDEX_HTML, UI_JS

router = APIRouter(tags=["ui"], include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """Serve the lightweight debug UI."""
    return HTMLResponse(INDEX_HTML)


@router.get("/ui.js", response_class=PlainTextResponse)
async def ui_js() -> PlainTextResponse:
    """Serve the lightweight debug UI script."""
    return PlainTextResponse(content=UI_JS, media_type="application/javascript")
