"""Service layer for chat invocation and stream normalization."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

from api.contracts import ChatRequest
from core.agent.contracts import DeepAgentInvokeRequest, DeepAgentInvokeResponse
from factory import build_default_deep_agent_orchestrator


class ChatService:
    """Coordinate HTTP chat requests with the deep-agent orchestrator."""

    def __init__(self) -> None:
        self._orchestrator_factory = build_default_deep_agent_orchestrator

    def invoke(self, request: ChatRequest) -> DeepAgentInvokeResponse:
        """Execute a normal chat request."""
        orchestrator = self._orchestrator_factory()
        return orchestrator.invoke(self._build_invoke_request(request, default_session_id="default-thread"))

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        """Yield SSE-compatible stream chunks for a chat request."""
        orchestrator = self._orchestrator_factory()
        try:
            stream = orchestrator.stream(
                self._build_invoke_request(
                    request,
                    default_session_id=f"stream-{uuid.uuid4()}",
                )
            )
            for event in stream:
                content = self._normalize_event(event)
                if content:
                    yield self._serialize_event({"content": content})
            yield self._serialize_event({"done": True})
        except Exception as exc:  # noqa: BLE001
            yield self._serialize_event({"error": str(exc)})

    @staticmethod
    def _build_invoke_request(request: ChatRequest, *, default_session_id: str) -> DeepAgentInvokeRequest:
        """Convert HTTP request payloads into deep-agent invoke requests."""
        return DeepAgentInvokeRequest(
            user_input=request.messages[-1].content,
            session_id=request.conversation_id or default_session_id,
            model=request.model,
        )

    @staticmethod
    def _normalize_event(event: Any) -> str:
        """Normalize deep-agent events into text chunks."""
        if isinstance(event, tuple) and len(event) == 2:
            # Deep Agents stream events often arrive as (chunk, metadata); UI only needs text.
            chunk, metadata = event
            content = getattr(chunk, "content", None)
            if isinstance(content, list):
                return "".join(str(item) for item in content if item)
            if content:
                return str(content)
            return json.dumps(metadata, ensure_ascii=False)
        if isinstance(event, dict):
            return json.dumps(event, ensure_ascii=False)
        return str(event)

    @staticmethod
    def _serialize_event(payload: dict[str, Any]) -> str:
        """Serialize an SSE payload."""
        return "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"
