"""Tool abstractions for the standalone Deep Agents service."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class ToolParameter(BaseModel):
    """Simplified JSON schema-like parameter definition."""

    name: str
    type: str = "string"
    description: str = ""
    required: bool = True


class BaseTool(ABC):
    """Common base class for service tools."""

    name: str = "base_tool"
    description: str = "基础工具"

    def __init__(self) -> None:
        self.parameters: list[ToolParameter] = []

    def schema_parameters(self) -> dict[str, Any]:
        """Export OpenAI-style parameter schema."""
        properties: dict[str, Any] = {}
        required: list[str] = []
        for param in self.parameters:
            properties[param.name] = {"type": param.type, "description": param.description}
            if param.required:
                required.append(param.name)
        return {"type": "object", "properties": properties, "required": required}

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute tool logic."""
