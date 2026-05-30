from __future__ import annotations

import json

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, *, name: str, arguments_json: str) -> str:
        try:
            arguments = json.loads(arguments_json)
        except json.JSONDecodeError as error:
            raise ToolRunError(f"invalid JSON arguments for tool {name}") from error
        if not isinstance(arguments, dict):
            raise ToolRunError(f"tool {name} arguments must be a JSON object")

        tool = self._registry.get(name)
        try:
            return tool.execute(arguments)
        except ToolRunError:
            raise
        except Exception as error:
            raise ToolRunError(f"tool {name} failed") from error
