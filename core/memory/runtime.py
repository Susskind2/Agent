"""Memory/backends helpers for Deep Agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import DeepAgentSettings


def build_memory_file_seed(settings: DeepAgentSettings) -> dict[str, Any]:
    """
    Seed initial memory files for the deep agent.

    This mirrors Deep Agents' memory-files pattern. If `deepagents` is not installed yet,
    this function still returns a plain mapping that can later be transformed with
    `create_file_data(...)` at runtime.
    """
    _ = settings
    project_summary = (
        "# AGENTS\n\n"
        "这是一个企业级 AI Agent 服务项目。\n\n"
        "关键目标：\n"
        "- 提供对话、工具调用、RAG 与文档管理能力\n"
        "- 优先使用真实工具和知识库，不要凭空编造\n"
        "- 对数据库和高风险工具操作保持谨慎\n"
    )
    preferences = (
        "# Preferences\n\n"
        "- 默认输出中文\n"
        "- 复杂任务先规划再执行\n"
        "- 如果上下文不足，应明确说明限制\n"
    )
    return {
        "/memories/AGENTS.md": project_summary,
        "/memories/preferences.md": preferences,
    }


def build_backend(settings: DeepAgentSettings, store: Any | None = None):
    """
    Build a Deep Agents backend.

    - If no store is provided, use the default ephemeral StateBackend.
    - If a store is provided, route `/memories/` to persistent storage.
    """
    _ = settings
    from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

    if store is None:
        return lambda runtime: StateBackend(runtime)

    return lambda runtime: CompositeBackend(
        default=StateBackend(runtime),
        routes={
            "/memories/": StoreBackend(runtime, namespace=lambda ctx: (ctx.runtime.context.user_id,)),
        },
    )


def ensure_workspace(settings: DeepAgentSettings) -> Path:
    """Ensure the optional local workspace directory exists."""
    settings.workspace_path.mkdir(parents=True, exist_ok=True)
    return settings.workspace_path
