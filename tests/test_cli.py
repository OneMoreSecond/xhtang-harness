from __future__ import annotations

import pytest

from xhtang_harness import __version__
from xhtang_harness.cli import DEFAULT_GOAL, main, render_demo


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
