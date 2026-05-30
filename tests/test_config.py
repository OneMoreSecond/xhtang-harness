from __future__ import annotations

from pathlib import Path

import pytest

from xhtang_harness.config import ConfigOverrides, load_config
from xhtang_harness.errors import ConfigError


def test_default_state_path_is_worktree_local(tmp_path: Path) -> None:
    first = load_config(prompt="hello", env={}, cwd=tmp_path / "one")
    second = load_config(prompt="hello", env={}, cwd=tmp_path / "two")

    assert first.state_path == tmp_path / "one" / ".xhtang-harness" / "state.sqlite3"
    assert second.state_path == tmp_path / "two" / ".xhtang-harness" / "state.sqlite3"


def test_config_precedence_uses_cli_before_env(tmp_path: Path) -> None:
    config = load_config(
        prompt="hello",
        overrides=ConfigOverrides(
            thinking="disabled",
            state_path=tmp_path / "cli.sqlite3",
            skill_learning="auto",
            skills_path=tmp_path / "cli-skills",
        ),
        env={
            "XHTANG_HARNESS_THINKING": "enabled",
            "XHTANG_HARNESS_STATE_PATH": str(tmp_path / "env.sqlite3"),
            "XHTANG_HARNESS_SKILL_LEARNING": "suggest",
            "XHTANG_HARNESS_SKILLS_PATH": str(tmp_path / "env-skills"),
            "DEEPSEEK_MODEL": "deepseek-v4-flash",
        },
        cwd=tmp_path,
    )

    assert config.thinking == "disabled"
    assert config.reasoning_effort is None
    assert config.state_path == tmp_path / "cli.sqlite3"
    assert config.skill_learning == "auto"
    assert config.skills_path == tmp_path / "cli-skills"
    assert config.model == "deepseek-v4-flash"


def test_invalid_thinking_mode_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="thinking must be enabled or disabled"):
        load_config(
            prompt="hello",
            overrides=ConfigOverrides(thinking="sometimes"),
            env={},
            cwd=tmp_path,
        )


def test_invalid_reasoning_effort_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="reasoning effort must be high or max"):
        load_config(
            prompt="hello",
            overrides=ConfigOverrides(reasoning_effort="low"),
            env={},
            cwd=tmp_path,
        )


def test_default_skills_path_is_worktree_local(tmp_path: Path) -> None:
    config = load_config(prompt="hello", env={}, cwd=tmp_path)

    assert config.skill_learning == "off"
    assert config.skills_path == tmp_path / ".skills"


def test_invalid_skill_learning_mode_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(
        ConfigError,
        match="skill learning must be off, suggest, or auto",
    ):
        load_config(
            prompt="hello",
            overrides=ConfigOverrides(skill_learning="always"),
            env={},
            cwd=tmp_path,
        )
