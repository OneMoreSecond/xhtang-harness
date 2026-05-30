from __future__ import annotations

import pytest

from xhtang_harness.conversation import Message, ToolCall, new_id


def test_new_id_includes_prefix() -> None:
    assert new_id("run").startswith("run_")


def test_tool_message_requires_tool_call_id() -> None:
    with pytest.raises(ValueError, match="tool messages require tool_call_id"):
        Message(role="tool", content="done")


def test_assistant_message_can_preserve_reasoning_and_tool_calls() -> None:
    message = Message(
        role="assistant",
        content=None,
        reasoning_content="private",
        tool_calls=(ToolCall(id="call_1", name="get_current_time", arguments="{}"),),
    )

    assert message.reasoning_content == "private"
    assert message.tool_calls[0].name == "get_current_time"
