from __future__ import annotations

import pytest

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.registry import ToolDefinition, ToolRegistry


def make_tool(name: str = "echo") -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description="Echo test tool.",
        parameters={"type": "object"},
        execute=lambda arguments: str(arguments["value"]),
    )


def test_registry_returns_provider_tool_schema() -> None:
    registry = ToolRegistry((make_tool(),))

    assert registry.provider_tools() == [
        {
            "type": "function",
            "function": {
                "name": "echo",
                "description": "Echo test tool.",
                "parameters": {"type": "object"},
            },
        }
    ]


def test_registry_rejects_unknown_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(ToolRunError, match="unknown tool: missing"):
        registry.get("missing")


def test_registry_rejects_duplicate_tool() -> None:
    with pytest.raises(ValueError, match="duplicate tool registered"):
        ToolRegistry((make_tool(), make_tool()))
