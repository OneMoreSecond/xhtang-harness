from __future__ import annotations

import sqlite3
from pathlib import Path

from xhtang_harness.conversation import Message, ProviderUsage, ToolCall
from xhtang_harness.events import HarnessEvent
from xhtang_harness.storage.sqlite import SQLiteStore


def test_sqlite_store_persists_run_history_and_events(tmp_path: Path) -> None:
    with SQLiteStore(tmp_path / "state.sqlite3") as store:
        session = store.create_session("Demo")
        run = store.start_run(session.id)
        assistant = Message(
            role="assistant",
            content=None,
            reasoning_content="private",
            tool_calls=(
                ToolCall(
                    id="call_1",
                    name="get_current_time",
                    arguments='{"timezone": "UTC"}',
                ),
            ),
        )

        store.add_message(session.id, run.id, Message(role="user", content="hello"))
        store.add_message(session.id, run.id, assistant)
        store.record_usage(
            run.id,
            ProviderUsage(
                prompt_tokens=1,
                completion_tokens=2,
                reasoning_tokens=3,
                prompt_cache_hit_tokens=4,
                prompt_cache_miss_tokens=5,
            ),
        )
        store.record_event(run.id, HarnessEvent("run_started", {"run_id": run.id}))
        store.complete_run(run.id)

        messages = store.load_messages(session.id)
        events = store.events_for_run(run.id)

    assert messages[0].role == "user"
    assert messages[1].reasoning_content == "private"
    assert messages[1].tool_calls[0].name == "get_current_time"
    assert events == (HarnessEvent("run_started", {"run_id": run.id}),)
    assert SQLiteStore(tmp_path / "state.sqlite3").run_status(run.id) == "completed"


def test_sqlite_store_allows_two_connections_to_write(tmp_path: Path) -> None:
    path = tmp_path / "shared.sqlite3"
    with SQLiteStore(path) as first, SQLiteStore(path) as second:
        first_session = first.create_session("first")
        second_session = second.create_session("second")

    with sqlite3.connect(path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]

    assert first_session.id != second_session.id
    assert count == 2
