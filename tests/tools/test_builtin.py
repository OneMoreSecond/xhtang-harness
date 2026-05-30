from __future__ import annotations

from datetime import UTC, datetime

import pytest

from xhtang_harness.errors import ToolRunError
from xhtang_harness.tools.builtin import get_current_time_tool


def test_get_current_time_returns_injected_utc_time() -> None:
    tool = get_current_time_tool(clock=lambda: datetime(2026, 5, 30, 1, 2, tzinfo=UTC))

    assert tool.execute({}) == "2026-05-30T01:02:00+00:00"


def test_get_current_time_rejects_non_utc_timezone() -> None:
    tool = get_current_time_tool(clock=lambda: datetime(2026, 5, 30, tzinfo=UTC))

    with pytest.raises(ToolRunError, match="only supports timezone=UTC"):
        tool.execute({"timezone": "Asia/Shanghai"})
