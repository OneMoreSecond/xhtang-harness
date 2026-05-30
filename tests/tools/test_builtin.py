from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.builtin import (
    bash_tool,
    default_registry_tools,
    get_current_time_tool,
)


def test_get_current_time_returns_injected_utc_time() -> None:
    tool = get_current_time_tool(clock=lambda: datetime(2026, 5, 30, 1, 2, tzinfo=UTC))

    assert tool.execute({}) == "2026-05-30T01:02:00+00:00"


def test_get_current_time_rejects_non_utc_timezone() -> None:
    tool = get_current_time_tool(clock=lambda: datetime(2026, 5, 30, tzinfo=UTC))

    with pytest.raises(ToolRunError, match="only supports timezone=UTC"):
        tool.execute({"timezone": "Asia/Shanghai"})


def test_default_registry_tools_include_bash() -> None:
    names = [tool.name for tool in default_registry_tools()]

    assert names == ["get_current_time", "bash"]


def test_bash_tool_runs_command(tmp_path: Path) -> None:
    tool = bash_tool(cwd=tmp_path)

    result = tool.execute({"command": "printf hello"})

    assert '"exit_code": 0' in result
    assert '"stdout": "hello"' in result
    assert '"stderr": ""' in result


def test_bash_tool_reports_nonzero_exit(tmp_path: Path) -> None:
    tool = bash_tool(cwd=tmp_path)

    result = tool.execute({"command": "printf nope >&2; exit 7"})

    assert '"exit_code": 7' in result
    assert '"stderr": "nope"' in result


def test_bash_tool_uses_relative_cwd(tmp_path: Path) -> None:
    child = tmp_path / "child"
    child.mkdir()
    (child / "marker.txt").write_text("ok", encoding="utf-8")
    tool = bash_tool(cwd=tmp_path)

    result = tool.execute({"command": "pwd; cat marker.txt", "cwd": "child"})

    assert str(child) in result
    assert "ok" in result


def test_bash_tool_rejects_missing_command(tmp_path: Path) -> None:
    tool = bash_tool(cwd=tmp_path)

    with pytest.raises(ToolRunError, match="requires string argument command"):
        tool.execute({})


def test_bash_tool_rejects_missing_cwd(tmp_path: Path) -> None:
    tool = bash_tool(cwd=tmp_path)

    with pytest.raises(ToolRunError, match="cwd does not exist"):
        tool.execute({"command": "pwd", "cwd": "missing"})


def test_bash_tool_reports_timeout(tmp_path: Path) -> None:
    def timeout_runner(
        *args: object,
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd="bash", timeout=0.1)

    tool = bash_tool(cwd=tmp_path, runner=timeout_runner)

    with pytest.raises(ToolRunError, match="timed out"):
        tool.execute({"command": "sleep 1", "timeout_seconds": 0.1})
