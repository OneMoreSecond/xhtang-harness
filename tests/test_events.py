from __future__ import annotations

import json

from xhtang_harness.events import HarnessEvent


def test_event_json_line_is_machine_readable() -> None:
    line = HarnessEvent("run_started", {"run_id": "run_1"}).to_json_line()

    assert json.loads(line) == {
        "type": "run_started",
        "payload": {"run_id": "run_1"},
    }
