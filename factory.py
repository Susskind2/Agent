"""Factory helpers for wiring Deep Agents with the current project infrastructure."""

from __future__ import annotations

from typing import Any

from config import DeepAgentSettings
from core.agent.orchestrator import DeepAgentsOrchestrator
from core.tools.wiring import build_default_tool_registry
from infrastructure.database.session import async_session_factory
from infrastructure.llm.model_router import ModelConfig, ModelRouter


def build_model_router() -> ModelRouter:
    """Build a standalone model router from Deep Agent settings."""
    settings = DeepAgentSettings()
    cfg = ModelConfig(
        model_id=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base or None,
        priority=0,
        weight=1.0,
    )
    return ModelRouter([cfg])


def build_default_deep_agent_orchestrator(store: Any | None = None) -> DeepAgentsOrchestrator:
    """Create a Deep Agents orchestrator using the project's current infrastructure."""
    settings = DeepAgentSettings()
    model_router = build_model_router()
    tool_registry = build_default_tool_registry(session_factory=async_session_factory)
    return DeepAgentsOrchestrator(
        settings=settings,
        model_router=model_router,
        tool_registry=tool_registry,
        store=store,
    )
