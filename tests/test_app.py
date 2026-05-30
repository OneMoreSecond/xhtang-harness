from __future__ import annotations

from pathlib import Path

import pytest

from xhtang_harness.app import run_harness
from xhtang_harness.config import load_config
from xhtang_harness.errors import ConfigError


def test_run_harness_requires_api_key(tmp_path: Path) -> None:
    config = load_config(prompt="hello", env={}, cwd=tmp_path)

    with pytest.raises(ConfigError, match="DEEPSEEK_API_KEY"):
        tuple(run_harness(config))
