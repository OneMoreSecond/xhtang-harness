from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from xhtang_harness.errors import ToolRunError

ToolFunction = Callable[[Mapping[str, object]], str]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: Mapping[str, object]
    execute: ToolFunction

    def to_provider_tool(self) -> dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": dict(self.parameters),
            },
        }


class ToolRegistry:
    def __init__(self, tools: tuple[ToolDefinition, ...] = ()) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: ToolDefinition) -> None:
        if not tool.name.strip():
            raise ValueError("tool name must not be empty")
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as error:
            raise ToolRunError(f"unknown tool: {name}") from error

    def provider_tools(self) -> list[dict[str, object]]:
        return [tool.to_provider_tool() for tool in self._tools.values()]
