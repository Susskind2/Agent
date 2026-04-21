"""Subagent definitions for Deep Agents."""

from __future__ import annotations

from typing import Any

from .prompts import (
    DATA_SUBAGENT_PROMPT,
    RAG_SUBAGENT_PROMPT,
    RESEARCH_SUBAGENT_PROMPT,
)


def build_subagents(tool_registry: Any) -> list[dict[str, Any]]:
    """Create subagent definitions based on the available tool set."""
    all_tools = tool_registry.to_langchain_tools()
    name_to_tool = {tool.name: tool for tool in all_tools}

    research_tools = [tool for tool in all_tools if tool.name in {"web_search"}]
    data_tools = [tool for tool in all_tools if tool.name in {"calculator", "database_query"}]
    rag_tools = [tool for tool in all_tools if tool.name in {"web_search"}]

    return [
        {
            "name": "researcher",
            "description": "适合处理深度检索、资料调研和背景信息收集",
            "system_prompt": RESEARCH_SUBAGENT_PROMPT,
            "tools": research_tools or list(name_to_tool.values()),
        },
        {
            "name": "knowledge-rag",
            "description": "适合处理知识库问答、引用整理与证据压缩",
            "system_prompt": RAG_SUBAGENT_PROMPT,
            "tools": rag_tools or list(name_to_tool.values()),
        },
        {
            "name": "data-analyst",
            "description": "适合处理计算、结构化数据整理、数据库相关任务",
            "system_prompt": DATA_SUBAGENT_PROMPT,
            "tools": data_tools or list(name_to_tool.values()),
        },
    ]
