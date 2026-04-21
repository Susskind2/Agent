"""Minimal usage example for the Deep Agents implementation."""

from __future__ import annotations

from core.agent.contracts import DeepAgentInvokeRequest
from factory import build_default_deep_agent_orchestrator


def main() -> None:
    orchestrator = build_default_deep_agent_orchestrator()
    response = orchestrator.invoke(
        DeepAgentInvokeRequest(
            user_input="请先拆解一个企业知识问答系统的开发任务，再给出实施建议。",
            session_id="demo-thread-1",
        )
    )
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
