from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.registry import ToolDefinition

_DEFAULT_BASH_TIMEOUT_SECONDS = 10.0
_MAX_BASH_TIMEOUT_SECONDS = 60.0
_MAX_CAPTURED_OUTPUT_CHARS = 12_000


def bash_tool(
    *,
    cwd: Path | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> ToolDefinition:
    active_cwd = cwd if cwd is not None else Path.cwd()
    active_runner = runner if runner is not None else subprocess.run

    def execute(arguments: Mapping[str, object]) -> str:
        command = _required_string_argument(arguments, "command", tool_name="bash")
        timeout_seconds = _timeout_seconds(arguments.get("timeout_seconds"))
        working_directory = _working_directory(arguments, active_cwd)

        try:
            result = active_runner(
                ["/bin/bash", "-lc", command],
                cwd=working_directory,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise ToolRunError(
                f"bash command timed out after {timeout_seconds:g} seconds"
            ) from error
        except OSError as error:
            raise ToolRunError(f"bash command could not start: {error}") from error

        stdout = _trim_output(result.stdout)
        stderr = _trim_output(result.stderr)
        return json.dumps(
            {
                "exit_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    return ToolDefinition(
        name="bash",
        description=(
            "Run a local bash command in the current harness worktree and return "
            "exit_code, stdout, and stderr. Use for read-only inspection unless "
            "the user explicitly asks for changes."
        ),
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to run with /bin/bash -lc.",
                },
                "cwd": {
                    "type": "string",
                    "description": (
                        "Optional working directory. Defaults to the harness cwd."
                    ),
                },
                "timeout_seconds": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": _MAX_BASH_TIMEOUT_SECONDS,
                    "description": "Optional timeout in seconds. Defaults to 10.",
                },
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        execute=execute,
    )


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
    return (get_current_time_tool(), bash_tool())


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _required_string_argument(
    arguments: Mapping[str, object],
    name: str,
    *,
    tool_name: str,
) -> str:
    value = arguments.get(name)
    if not isinstance(value, str):
        raise ToolRunError(f"{tool_name} requires string argument {name}")
    if not value.strip():
        raise ToolRunError(f"{tool_name} argument {name} must not be empty")
    return value


def _timeout_seconds(value: object) -> float:
    if value is None:
        return _DEFAULT_BASH_TIMEOUT_SECONDS
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ToolRunError("bash timeout_seconds must be a number")

    timeout = float(value)
    if timeout <= 0 or timeout > _MAX_BASH_TIMEOUT_SECONDS:
        raise ToolRunError(
            f"bash timeout_seconds must be between 0 and {_MAX_BASH_TIMEOUT_SECONDS:g}"
        )
    return timeout


def _working_directory(arguments: Mapping[str, object], default_cwd: Path) -> Path:
    cwd_value = arguments.get("cwd")
    if cwd_value is None:
        return default_cwd
    if not isinstance(cwd_value, str):
        raise ToolRunError("bash cwd must be a string")
    if not cwd_value.strip():
        raise ToolRunError("bash cwd must not be empty")

    path = Path(cwd_value).expanduser()
    if not path.is_absolute():
        path = default_cwd / path
    if not path.exists():
        raise ToolRunError(f"bash cwd does not exist: {path}")
    if not path.is_dir():
        raise ToolRunError(f"bash cwd is not a directory: {path}")
    return path


def _trim_output(output: str) -> str:
    if len(output) <= _MAX_CAPTURED_OUTPUT_CHARS:
        return output
    return output[:_MAX_CAPTURED_OUTPUT_CHARS] + "\n[output truncated]"
