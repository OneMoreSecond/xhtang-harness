from __future__ import annotations

import pytest

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.executor import ToolExecutor
from xhtang_harness.tools.registry import ToolDefinition, ToolRegistry


def test_executor_validates_and_runs_json_arguments() -> None:
    registry = ToolRegistry(
        (
            ToolDefinition(
                name="echo",
                description="Echo value.",
                parameters={"type": "object"},
                execute=lambda arguments: str(arguments["value"]),
            ),
        )
    )

    result = ToolExecutor(registry).execute(
        name="echo",
        arguments_json='{"value": "ok"}',
    )

    assert result == "ok"


def test_executor_rejects_invalid_json() -> None:
    executor = ToolExecutor(ToolRegistry())

    with pytest.raises(ToolRunError, match="invalid JSON arguments"):
        executor.execute(name="echo", arguments_json="{")


def test_executor_rejects_non_object_arguments() -> None:
    executor = ToolExecutor(ToolRegistry())

    with pytest.raises(ToolRunError, match="must be a JSON object"):
        executor.execute(name="echo", arguments_json="[]")
