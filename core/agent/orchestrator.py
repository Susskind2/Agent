"""Deep Agents based orchestrator."""

from __future__ import annotations

from typing import Any

from deepagents import create_deep_agent

from config import DeepAgentSettings
from core.agent.contracts import DeepAgentInvokeRequest, DeepAgentInvokeResponse
from core.memory.runtime import build_backend, build_memory_file_seed, ensure_workspace
from .prompts import MAIN_SYSTEM_PROMPT
from .subagents import build_subagents
from core.tools.wiring import build_interrupt_policy

try:
    from langgraph.checkpoint.memory import InMemorySaver as MemorySaver
except ImportError:  # pragma: no cover
    from langgraph.checkpoint.memory import MemorySaver  # type: ignore[no-redef]


class DeepAgentsOrchestrator:
    """
    Wrap Deep Agents in a project-friendly orchestrator.

    This version keeps infrastructure injection points explicit so the API layer,
    routing layer, and storage layer can evolve independently.
    """

    def __init__(
        self,
        settings: DeepAgentSettings,
        model_router: Any,
        tool_registry: Any,
        *,
        store: Any | None = None,
        checkpointer: Any | None = None,
    ) -> None:
        self.settings = settings
        self.model_router = model_router
        self.tool_registry = tool_registry
        self.store = store
        self.checkpointer = checkpointer or MemorySaver()
        self._agent = None

    def build_agent(self, model_preference: str | None = None):
        """Build and cache the deep agent graph."""
        if self._agent is not None:
            return self._agent

        ensure_workspace(self.settings)
        model = self.model_router.get_llm(
            self.settings.deep_agent_model_purpose,
            model_preference=model_preference,
        )
        interrupt_on = build_interrupt_policy(
            self.tool_registry,
            enable_human_approval=self.settings.deep_agent_enable_human_approval,
        )
        subagents = build_subagents(self.tool_registry) if self.settings.deep_agent_use_subagents else []

        self._agent = create_deep_agent(
            name=self.settings.deep_agent_name,
            model=model,
            tools=self.tool_registry.to_langchain_tools(),
            system_prompt=MAIN_SYSTEM_PROMPT + "\n\n" + self.settings.deep_agent_system_prompt,
            subagents=subagents,
            interrupt_on=interrupt_on or None,
            memory=self.settings.deep_agent_memory_paths,
            backend=build_backend(self.settings, store=self.store),
            checkpointer=self.checkpointer,
            store=self.store,
        )
        return self._agent

    def build_initial_files(self) -> dict[str, Any]:
        """Build the initial file payload for Deep Agents memory files."""
        seed = build_memory_file_seed(self.settings)
        try:
            from deepagents.backends.utils import create_file_data

            return {path: create_file_data(content) for path, content in seed.items()}
        except Exception:
            return seed

    def invoke(self, request: DeepAgentInvokeRequest) -> DeepAgentInvokeResponse:
        """Run the deep agent synchronously."""
        agent = self.build_agent(model_preference=request.model)
        thread_id = request.session_id
        user_id = request.user_id or self.settings.deep_agent_user_id
        files = request.files or self.build_initial_files()

        result = agent.invoke(
            {
                "messages": [{"role": "user", "content": request.user_input}],
                "files": files,
            },
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
        )
        answer = self._extract_answer(result)
        structured = result.get("structured_response") if isinstance(result, dict) else None
        todos = result.get("todos", []) if isinstance(result, dict) else []
        return DeepAgentInvokeResponse(
            success=True,
            answer=answer,
            thread_id=thread_id,
            raw=result if isinstance(result, dict) else {"result": result},
            structured_response=structured,
            todos=todos,
        )

    def stream(self, request: DeepAgentInvokeRequest):
        """Stream the deep agent execution for UI or API adapters."""
        agent = self.build_agent(model_preference=request.model)
        thread_id = request.session_id
        user_id = request.user_id or self.settings.deep_agent_user_id
        files = request.files or self.build_initial_files()
        return agent.stream(
            {
                "messages": [{"role": "user", "content": request.user_input}],
                "files": files,
            },
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            stream_mode=["updates", "messages", "custom"],
        )

    @staticmethod
    def _extract_answer(result: Any) -> str:
        """Extract the last assistant answer from a deep-agent result state."""
        if not isinstance(result, dict):
            return str(result)
        messages = result.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", None)
            if content:
                return str(content)
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                return str(msg.get("content", ""))
        return ""
