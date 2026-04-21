"""Health-check routes."""

from __future__ import annotations

from fastapi import APIRouter

from config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight health response."""
    settings = get_settings()
    return {"status": "ok", "service": settings.app_name}
