from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

EventType = Literal[
    "run_started",
    "message_recorded",
    "provider_request_started",
    "answer_delta",
    "tool_call_started",
    "tool_call_finished",
    "retry_scheduled",
    "run_completed",
    "run_failed",
    "run_cancelled",
]


@dataclass(frozen=True)
class HarnessEvent:
    type: EventType
    payload: dict[str, object]

    def to_json_line(self) -> str:
        return json.dumps(
            {"type": self.type, "payload": self.payload},
            ensure_ascii=False,
            sort_keys=True,
        )
