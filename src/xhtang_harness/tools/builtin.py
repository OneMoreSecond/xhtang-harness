from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.registry import ToolDefinition


def get_current_time_tool(
    *,
    clock: Callable[[], datetime] | None = None,
) -> ToolDefinition:
    active_clock = clock if clock is not None else _utc_now

    def execute(arguments: Mapping[str, object]) -> str:
        timezone = arguments.get("timezone", "UTC")
        if timezone != "UTC":
            raise ToolRunError("get_current_time only supports timezone=UTC")
        return active_clock().astimezone(UTC).isoformat()

    return ToolDefinition(
        name="get_current_time",
        description="Return the current time in UTC as an ISO-8601 timestamp.",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "enum": ["UTC"],
                    "description": "Timezone for the returned timestamp.",
                }
            },
            "additionalProperties": False,
        },
        execute=execute,
    )


def default_registry_tools() -> tuple[ToolDefinition, ...]:
    return (get_current_time_tool(),)


def _utc_now() -> datetime:
    return datetime.now(UTC)
