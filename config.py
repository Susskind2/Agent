"""Configuration for the Deep Agents implementation."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepAgentSettings(BaseSettings):
    """Settings dedicated to the `agents/` deep-agents implementation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deep_agent_name: str = Field(default="enterprise-deep-agent")
    app_name: str = Field(default="enterprise-deep-agent-service")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)

    openai_api_key: str = Field(default="", description="OpenAI-compatible API key")
    openai_api_base: str = Field(default="https://api.openai.com/v1")
    openai_model: str = Field(default="gpt-4o-mini")
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agent_db",
        description="Async SQLAlchemy database URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    milvus_host: str = Field(default="localhost")
    milvus_port: int = Field(default=19530)
    milvus_user: str = Field(default="")
    milvus_password: str = Field(default="")
    milvus_collection_name: str = Field(default="agent_knowledge")

    deep_agent_model_purpose: str = Field(default="deep_agent")
    deep_agent_system_prompt: str = Field(
        default=(
            "你是企业级智能代理总控。优先拆解任务、调用工具、查阅上下文，再给出可靠答案。"
            "涉及数据库、知识库或外部检索时，优先使用工具，不要凭空臆测。"
        )
    )
    deep_agent_use_subagents: bool = Field(default=True)
    deep_agent_enable_human_approval: bool = Field(default=True)
    deep_agent_memory_paths: list[str] = Field(
        default_factory=lambda: [
            "/memories/AGENTS.md",
            "/memories/preferences.md",
        ]
    )
    deep_agent_workspace_dir: str = Field(default="./agents/workspace")
    deep_agent_user_id: str = Field(default="local-user")

    @property
    def workspace_path(self) -> Path:
        return Path(self.deep_agent_workspace_dir).resolve()


@lru_cache(maxsize=1)
def get_settings() -> DeepAgentSettings:
    """Return a cached settings instance for application wiring."""
    return DeepAgentSettings()
