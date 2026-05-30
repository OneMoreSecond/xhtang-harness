from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from xhtang_harness import __version__
from xhtang_harness.cli import DEFAULT_GOAL, main, render_demo

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_render_demo_uses_default_goal() -> None:
    output = render_demo(DEFAULT_GOAL)

    assert "xhtang-harness demo" in output
    assert f"version: {__version__}" in output
    assert f"goal: {DEFAULT_GOAL}" in output
    assert "status: ready" in output


def test_render_demo_trims_goal() -> None:
    output = render_demo("  Build the harness  ")

    assert "goal: Build the harness" in output


def test_render_demo_rejects_blank_goal() -> None:
    with pytest.raises(ValueError, match="goal must not be empty"):
        render_demo(" ")


def test_main_prints_demo(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["Test goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "goal: Test goal" in captured.out


def test_local_command_entry_runs_from_checkout() -> None:
    completed = subprocess.run(
        [str(REPO_ROOT / "bin" / "xhtang-harness"), "Worktree goal"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "goal: Worktree goal" in completed.stdout
