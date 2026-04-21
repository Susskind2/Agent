"""Tool registry for the standalone Deep Agents service."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from loguru import logger
from pydantic import Field, create_model

from .base import BaseTool


class ToolRegistry:
    """Manage all available tools and export them as LangChain tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            logger.warning("Tool [{}] already exists and will be overwritten", tool.name)
        self._tools[tool.name] = tool
        logger.info("Registered tool: {}", tool.name)

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def get_all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def list_tool_names(self) -> list[str]:
        return list(self._tools.keys())

    async def invoke(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self.get_tool(name)
        result = await tool.execute(**arguments)
        return result if isinstance(result, str) else str(result)

    def to_langchain_tools(self, allowed_names: list[str] | None = None) -> list[StructuredTool]:
        tools = self.get_all_tools()
        if allowed_names is not None:
            allowed = set(allowed_names)
            tools = [tool for tool in tools if tool.name in allowed]
        return [self._to_langchain_tool(tool) for tool in tools]

    def _to_langchain_tool(self, tool: BaseTool) -> StructuredTool:
        fields: dict[str, tuple[type[Any], Field]] = {}
        type_map: dict[str, type[Any]] = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
        }
        for param in tool.parameters:
            py_type = type_map.get(param.type, str)
            default = ... if param.required else None
            fields[param.name] = (py_type, Field(default=default, description=param.description or ""))
        args_schema = create_model(f"{tool.name.title().replace('_', '')}Args", **fields)

        async def _arun(**kwargs: Any) -> str:
            result = await tool.execute(**kwargs)
            return result if isinstance(result, str) else str(result)

        return StructuredTool.from_function(
            coroutine=_arun,
            name=tool.name,
            description=tool.description,
            args_schema=args_schema,
        )
