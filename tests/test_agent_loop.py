from __future__ import annotations

from pathlib import Path

from xhtang_harness.agent_loop import AgentLoop
from xhtang_harness.config import ConfigOverrides, load_config
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
        self.requests: list[tuple[object, object]] = []

    def complete(self, messages: object, options: object) -> DeepSeekResponse:
        self.message_counts.append(len(messages))
        self.requests.append((messages, options))
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


def test_agent_loop_loads_matching_local_skill_body(tmp_path: Path) -> None:
    description = "Use when the prompt says azure orchid ledger."
    secret = "secret-value: tangerine-cascade-492"
    skill_dir = tmp_path / ".skills" / "orchid-ledger"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: orchid-ledger",
                f"description: {description}",
                "---",
                "",
                "When this skill is active, answer with:",
                secret,
            ]
        ),
        encoding="utf-8",
    )
    config = load_config(prompt=description, env={}, cwd=tmp_path)
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content=secret,
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
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

    first_messages = provider.requests[0][0]
    assert isinstance(first_messages, tuple)
    assert first_messages[0].role == "system"
    assert secret in str(first_messages[0].content)
    assert "skill_context_loaded" in [event.type for event in events]


def test_agent_loop_continues_session_after_skill_secret_round(tmp_path: Path) -> None:
    description = "Use when the prompt says silver compass memory check."
    secret = "hidden-secret: saffron-vector-8842"
    skill_dir = tmp_path / ".skills" / "silver-compass"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: silver-compass",
                f"description: {description}",
                "---",
                "",
                "When this skill is active, answer with:",
                secret,
            ]
        ),
        encoding="utf-8",
    )
    first_config = load_config(prompt=description, env={}, cwd=tmp_path)
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content=f"I read the local skill secret: {secret}",
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
            ),
            DeepSeekResponse(
                content=secret,
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
            ),
        )
    )
    registry = ToolRegistry()

    with SQLiteStore(first_config.state_path) as store:
        loop = AgentLoop(
            store=store,
            provider=provider,  # type: ignore[arg-type]
            registry=registry,
            executor=ToolExecutor(registry),
        )

        first_events = tuple(loop.run(config=first_config))
        session_id = str(first_events[0].payload["session_id"])
        second_config = load_config(
            prompt="What was the secret from the previous round?",
            overrides=ConfigOverrides(session=session_id),
            env={},
            cwd=tmp_path,
        )
        second_events = tuple(loop.run(config=second_config))

    first_messages = provider.requests[0][0]
    second_messages = provider.requests[1][0]
    assert isinstance(first_messages, tuple)
    assert isinstance(second_messages, tuple)
    assert first_messages[0].role == "system"
    assert secret in str(first_messages[0].content)
    assert [message.role for message in second_messages] == [
        "user",
        "assistant",
        "user",
    ]
    assert secret in str(second_messages[1].content)
    assert "skill_context_loaded" in [event.type for event in first_events]
    assert "skill_context_loaded" not in [event.type for event in second_events]


def test_agent_loop_reflects_on_skill_learning_suggest(tmp_path: Path) -> None:
    config = load_config(
        prompt="summarize reusable workflow",
        overrides=ConfigOverrides(skill_learning="suggest"),
        env={},
        cwd=tmp_path,
    )
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content="Done",
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
            ),
            DeepSeekResponse(
                content=(
                    '{"should_create": true, "reason": "Reusable.", '
                    '"skill_name": "workflow-note", '
                    '"description": "Use for workflow notes.", '
                    '"skill_body": "Keep notes concise."}'
                ),
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
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

    assert [event.type for event in events][-3:] == [
        "run_completed",
        "skill_learning_started",
        "skill_proposed",
    ]
    assert not (tmp_path / ".skills" / "workflow-note").exists()


def test_agent_loop_auto_writes_valid_skill(tmp_path: Path) -> None:
    config = load_config(
        prompt="make a reusable note",
        overrides=ConfigOverrides(skill_learning="auto"),
        env={},
        cwd=tmp_path,
    )
    provider = ScriptedProvider(
        (
            DeepSeekResponse(
                content="Done",
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
            ),
            DeepSeekResponse(
                content=(
                    '{"should_create": true, "reason": "Reusable.", '
                    '"skill_name": "reusable-note", '
                    '"description": "Use for reusable notes.", '
                    '"skill_body": "Write one clear note."}'
                ),
                reasoning_content=None,
                tool_calls=(),
                finish_reason="stop",
                usage=None,
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

    skill_file = tmp_path / ".skills" / "reusable-note" / "SKILL.md"
    assert skill_file.exists()
    assert "description: Use for reusable notes." in skill_file.read_text(
        encoding="utf-8"
    )
    assert events[-1].type == "skill_written"
