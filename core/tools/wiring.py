"""Tool assembly for the Deep Agents implementation."""

from __future__ import annotations

from typing import Any

from .builtin import CalculatorTool, DatabaseQueryTool, WebSearchTool
from .registry import ToolRegistry


def build_default_tool_registry(session_factory: Any | None = None) -> ToolRegistry:
    """Create a tool registry aligned with the existing project tool set."""
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    if session_factory is not None:
        registry.register(DatabaseQueryTool(session_factory=session_factory))
    return registry


def build_interrupt_policy(tool_registry: ToolRegistry, enable_human_approval: bool = True) -> dict[str, Any]:
    """
    Build a default interrupt policy for Deep Agents.

    We only require approval for riskier tools by default.
    """
    if not enable_human_approval:
        return {}

    policy: dict[str, Any] = {}
    for tool_name in tool_registry.list_tool_names():
        if tool_name in {"database_query"}:
            policy[tool_name] = {"allowed_decisions": ["approve", "reject", "edit"]}
        else:
            policy[tool_name] = False
    return policy
