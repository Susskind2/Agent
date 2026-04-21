"""Chat API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.contracts import ChatRequest
from services.chat import ChatService

router = APIRouter(tags=["chat"])
_chat_service = ChatService()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Invoke the standalone deep agent."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    return _chat_service.invoke(request).model_dump()


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream deep-agent output as SSE-compatible chunks."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    return StreamingResponse(
        _chat_service.stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
