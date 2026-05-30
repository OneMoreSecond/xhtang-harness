from __future__ import annotations

import io
import sys
from collections.abc import Iterator

import pytest

from xhtang_harness.cli import main
from xhtang_harness.config import HarnessConfig
from xhtang_harness.events import HarnessEvent


class InteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return True


class NonInteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return False


def test_main_prompts_for_missing_initial_goal(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen_config: HarnessConfig | None = None

    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        nonlocal seen_config
        seen_config = config
        yield HarnessEvent("run_started", {"run_id": "run_1", "session_id": "ses_1"})
        yield HarnessEvent("run_completed", {"run_id": "run_1"})

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)
    monkeypatch.setattr(sys, "stdin", InteractiveInput("Prompt from input\n"))

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "initial goal:" in captured.err
    assert seen_config is not None
    assert seen_config.prompt == "Prompt from input"


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


def test_main_renders_bash_command_without_debug(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(config: HarnessConfig) -> Iterator[HarnessEvent]:
        yield HarnessEvent(
            "tool_call_started",
            {
                "tool_call_id": "call_1",
                "name": "bash",
                "command": "pwd",
            },
        )
        yield HarnessEvent("run_completed", {"run_id": "run_1"})

    monkeypatch.setattr("xhtang_harness.cli.run_harness", fake_run)

    exit_code = main(["Use bash to run pwd"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert 'tool_call_started: bash command="pwd"' in captured.out


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


def test_main_rejects_blank_initial_goal(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    exit_code = main([" "])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "config_error: prompt must not be empty" in captured.err


def test_main_rejects_blank_prompt_after_missing_goal(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(sys, "stdin", InteractiveInput("   \n"))

    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "initial goal:" in captured.err
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
