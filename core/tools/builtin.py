"""Builtin tools for the standalone Deep Agents service."""

from __future__ import annotations

import ast
import operator as op
from typing import Any

import httpx
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseTool, ToolParameter

_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
}


class CalculatorTool(BaseTool):
    """Safely evaluate arithmetic expressions."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "calculator"
        self.description = "计算数学表达式（加减乘除、幂、取模与括号）。"
        self.parameters = [
            ToolParameter(
                name="expression",
                type="string",
                description="仅包含数字与 + - * / ** % 和括号的表达式",
                required=True,
            )
        ]

    def _eval(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return float(_ALLOWED_OPS[type(node.op)](self._eval(node.left), self._eval(node.right)))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return float(_ALLOWED_OPS[type(node.op)](self._eval(node.operand)))
        if isinstance(node, ast.Expr):
            return self._eval(node.value)
        raise ValueError("不支持的表达式语法")

    async def execute(self, **kwargs: Any) -> str:
        expr = str(kwargs.get("expression", "")).strip()
        if not expr:
            raise ValueError("参数 expression 不能为空")
        tree = ast.parse(expr, mode="eval")
        result = self._eval(tree.body)
        logger.info("calculator {} = {}", expr, result)
        return str(result)


class WebSearchTool(BaseTool):
    """Lightweight web search tool using DuckDuckGo HTML results."""

    def __init__(self, timeout: float = 15.0) -> None:
        super().__init__()
        self.name = "web_search"
        self.description = "在互联网上搜索关键词并返回摘要文本。"
        self.parameters = [
            ToolParameter(name="query", type="string", description="搜索关键词或完整问句", required=True)
        ]
        self._timeout = timeout

    async def execute(self, **kwargs: Any) -> str:
        query = str(kwargs.get("query", "")).strip()
        if not query:
            raise ValueError("参数 query 不能为空")
        try:
            async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
                resp = await client.post("https://duckduckgo.com/html/", data={"q": query})
                resp.raise_for_status()
                return f"搜索「{query}」结果片段：\n{resp.text[:4000]}"
        except Exception as exc:
            logger.exception("web_search failed: {}", exc)
            return f"搜索暂时不可用，请稍后重试。错误: {exc!s}"


class DatabaseQueryTool(BaseTool):
    """Readonly SQL query tool."""

    def __init__(self, session_factory: Any | None = None) -> None:
        super().__init__()
        self.name = "database_query"
        self.description = "只读执行 SQL 查询并返回行列表。"
        self.parameters = [
            ToolParameter(name="sql", type="string", description="必须以 SELECT 开头的只读 SQL", required=True)
        ]
        self._session_factory = session_factory

    def _validate_sql(self, sql: str) -> str:
        safe_sql = sql.strip().rstrip(";")
        lower = safe_sql.lower()
        if not lower.startswith("select"):
            raise ValueError("仅允许 SELECT 查询")
        for word in ("insert", "update", "delete", "drop", "alter", "truncate", "create"):
            if word in lower:
                raise ValueError(f"查询包含禁止关键字: {word}")
        return safe_sql

    async def execute(self, **kwargs: Any) -> Any:
        sql = str(kwargs.get("sql", "")).strip()
        if not sql:
            raise ValueError("参数 sql 不能为空")
        safe_sql = self._validate_sql(sql)

        session: AsyncSession | None = kwargs.get("session")
        if session is None and self._session_factory is None:
            raise RuntimeError("未提供 session 且未配置 session_factory")

        async def _run(sess: AsyncSession) -> list[dict[str, Any]]:
            result = await sess.execute(text(safe_sql))
            return [dict(row) for row in result.mappings().all()]

        if session is not None:
            return await _run(session)

        async with self._session_factory() as sess:  # type: ignore[misc]
            return await _run(sess)
