"""HTTP request and response contracts for the standalone service."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """OpenAI-style chat message used by the API."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request body for chat and chat-stream endpoints."""

    messages: list[ChatMessage] = Field(min_length=1)
    conversation_id: str | None = None
    model: str | None = None
