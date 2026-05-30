from __future__ import annotations

from pathlib import Path

from xhtang_harness.agent_loop import AgentLoop
from xhtang_harness.config import load_config
from xhtang_harness.providers.deepseek import (
    DeepSeekResponse,
    DeepSeekToolCall,
    DeepSeekUsage,
)
from xhtang_harness.storage.sqlite import SQLiteStore
from xhtang_harness.tools.executor import ToolExecutor
from xhtang_harness.tools.registry import ToolDefinition, ToolRegistry


class ScriptedProvider:
    def __init__(self, responses: tuple[DeepSeekResponse, ...]) -> None:
        self.responses = list(responses)
        self.message_counts: list[int] = []

    def complete(self, messages: object, options: object) -> DeepSeekResponse:
        self.message_counts.append(len(messages))
        return self.responses.pop(0)


def test_agent_loop_persists_simple_answer(tmp_path: Path) -> None:
    config = load_config(prompt="hello", env={}, cwd=tmp_path)
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content="Hello",
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=DeepSeekUsage(prompt_tokens=1, completion_tokens=2),
            ),
        )
    )
    registry = ToolRegistry()
    with SQLiteStore(config.state_path) as store:
        loop = AgentLoop(
            store=store,
            provider=provider,  # type: ignore[arg-type]
            registry=registry,
            executor=ToolExecutor(registry),
        )

        events = tuple(loop.run(config=config))

        run_id = events[0].payload["run_id"]
        session_id = events[0].payload["session_id"]
        messages = store.load_messages(str(session_id))

    assert [event.type for event in events] == [
        "run_started",
        "message_recorded",
        "provider_request_started",
        "message_recorded",
        "answer_delta",
        "run_completed",
    ]
    assert provider.message_counts == [1]
    assert messages[-1].content == "Hello"
    assert run_id is not None


def test_agent_loop_executes_tool_and_replays_history(tmp_path: Path) -> None:
    config = load_config(prompt="what time is it", env={}, cwd=tmp_path)
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content="",
                reasoning_content="private",
                tool_calls=(
                    DeepSeekToolCall(
                        id="call_1",
                        name="fixed_time",
                        arguments="{}",
                    ),
                ),
                finish_reason="tool_calls",
                usage=None,
            ),
            DeepSeekResponse(
                content="It is noon.",
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
            ),
        )
    )
    registry = ToolRegistry(
        (
            ToolDefinition(
                name="fixed_time",
                description="Return fixed time.",
                parameters={"type": "object"},
                execute=lambda arguments: "2026-05-30T12:00:00+00:00",
            ),
        )
    )
    with SQLiteStore(config.state_path) as store:
        loop = AgentLoop(
            store=store,
            provider=provider,  # type: ignore[arg-type]
            registry=registry,
            executor=ToolExecutor(registry),
        )

        events = tuple(loop.run(config=config))
        session_id = str(events[0].payload["session_id"])
        messages = store.load_messages(session_id)

    assert "tool_call_started" in [event.type for event in events]
    assert "tool_call_finished" in [event.type for event in events]
    assert provider.message_counts == [1, 3]
    assert messages[1].reasoning_content == "private"
    assert messages[2].role == "tool"
    assert messages[-1].content == "It is noon."


def test_agent_loop_records_cancellation_before_provider_call(tmp_path: Path) -> None:
    config = load_config(prompt="hello", env={}, cwd=tmp_path)
    provider = ScriptedProvider(())
    registry = ToolRegistry()
    with SQLiteStore(config.state_path) as store:
        loop = AgentLoop(
            store=store,
            provider=provider,  # type: ignore[arg-type]
            registry=registry,
            executor=ToolExecutor(registry),
        )

        events = tuple(loop.run(config=config, cancel_requested=lambda: True))
        run_id = str(events[0].payload["run_id"])

        assert store.run_status(run_id) == "cancelled"

    assert events[-1].type == "run_cancelled"
    assert provider.message_counts == []
