"""Internal invoke contracts for the Deep Agents orchestrator."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeepAgentInvokeRequest(BaseModel):
    """Input contract for invoking the deep agent."""

    user_input: str
    session_id: str
    user_id: str | None = None
    model: str | None = None
    files: dict[str, Any] | None = None


class DeepAgentInvokeResponse(BaseModel):
    """High-level normalized response from the deep agent."""

    success: bool = True
    answer: str = ""
    thread_id: str
    raw: dict[str, Any] = Field(default_factory=dict)
    structured_response: dict[str, Any] | None = None
    todos: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
