from __future__ import annotations

from pathlib import Path

from xhtang_harness.config import load_config


def test_parallel_worktrees_get_separate_default_state_paths(tmp_path: Path) -> None:
    worktree_a = tmp_path / "repo-worktree-a"
    worktree_b = tmp_path / "repo-worktree-b"

    config_a = load_config(prompt="hello", env={}, cwd=worktree_a)
    config_b = load_config(prompt="hello", env={}, cwd=worktree_b)

    assert config_a.state_path != config_b.state_path
    assert config_a.state_path.parent == worktree_a / ".xhtang-harness"
    assert config_b.state_path.parent == worktree_b / ".xhtang-harness"
