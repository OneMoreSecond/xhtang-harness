from __future__ import annotations

import io
import sys
from collections.abc import Iterator

import pytest

from xhtang_harness import __version__
from xhtang_harness.cli import DEFAULT_GOAL, main, render_demo
from xhtang_harness.config import HarnessConfig
from xhtang_harness.events import HarnessEvent


class InteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return True


class NonInteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return False


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


def test_main_renders_harness_events(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_config: HarnessConfig | None = None

    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        nonlocal seen_config
        seen_config = config
        yield HarnessEvent("run_started", {"run_id": "run_1", "session_id": "ses_1"})
        yield HarnessEvent("answer_delta", {"text": "Done"})
        yield HarnessEvent("run_completed", {"run_id": "run_1"})

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)

    exit_code = main(["Test goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "run_started: run_1 session=ses_1" in captured.out
    assert "answer_delta: Done" in captured.out
    assert "run_completed: run_1" in captured.out
    assert seen_config is not None
    assert seen_config.prompt == "Test goal"


def test_main_renders_skill_learning_status(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_config: HarnessConfig | None = None

    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        nonlocal seen_config
        seen_config = config
        yield HarnessEvent(
            "skill_learning_started",
            {"run_id": "run_1", "mode": config.skill_learning},
        )
        yield HarnessEvent(
            "skill_written",
            {
                "run_id": "run_1",
                "skill_name": "demo-skill",
                "target_path": ".skills/demo-skill",
                "file_count": 1,
            },
        )

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)

    exit_code = main(["--skill-learning", "auto", "Test goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "skill_learning_started: thinking whether to create a skill" in captured.out
    assert "skill_written: demo-skill" in captured.out
    assert seen_config is not None
    assert seen_config.skill_learning == "auto"


def test_main_reads_additional_prompt_after_skill_learning(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_configs: list[HarnessConfig] = []

    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        seen_configs.append(config)
        run_id = f"run_{len(seen_configs)}"
        session_id = config.session or "ses_1"
        yield HarnessEvent("run_started", {"run_id": run_id, "session_id": session_id})
        yield HarnessEvent("run_completed", {"run_id": run_id})
        yield HarnessEvent(
            "skill_learning_started",
            {"run_id": run_id, "mode": config.skill_learning},
        )

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)
    monkeypatch.setattr(sys, "stdin", InteractiveInput("Second goal\n\n"))

    exit_code = main(["--skill-learning", "suggest", "First goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert [config.prompt for config in seen_configs] == ["First goal", "Second goal"]
    assert [config.session for config in seen_configs] == [None, "ses_1"]
    assert captured.out.count("skill_learning_started") == 2
    assert captured.err.count("additional prompt (blank to exit):") == 2


def test_main_skips_additional_prompt_when_stdin_is_not_interactive(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_configs: list[HarnessConfig] = []

    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        seen_configs.append(config)
        yield HarnessEvent("run_started", {"run_id": "run_1", "session_id": "ses_1"})
        yield HarnessEvent("run_completed", {"run_id": "run_1"})

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)
    monkeypatch.setattr(sys, "stdin", NonInteractiveInput("Second goal\n"))

    exit_code = main(["First goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert [config.prompt for config in seen_configs] == ["First goal"]
    assert "additional prompt" not in captured.err


def test_main_renders_config_errors(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    exit_code = main([" "])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "config_error: prompt must not be empty" in captured.err


def test_main_no_stream_still_prints_final_answer(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        yield HarnessEvent("answer_delta", {"text": "Final answer"})
        yield HarnessEvent("run_completed", {"run_id": "run_1"})

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)

    exit_code = main(["--no-stream", "Test goal"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "answer_delta: Final answer" in captured.out
