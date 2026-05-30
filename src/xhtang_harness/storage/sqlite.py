from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from xhtang_harness.conversation import (
    Message,
    ProviderUsage,
    Run,
    Session,
    ToolCall,
    new_id,
)
from xhtang_harness.errors import StorageError
from xhtang_harness.events import HarnessEvent


@dataclass(frozen=True)
class StoredToolCall:
    id: str
    provider_tool_call_id: str
    name: str
    arguments_json: str
    status: str
    result_text: str | None
    error_message: str | None


class SQLiteStore(AbstractContextManager["SQLiteStore"]):
    def __init__(self, path: Path, *, timeout: float = 5.0) -> None:
        self.path = path
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(self.path, timeout=timeout)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA busy_timeout = 5000")
            self._create_schema()
        except sqlite3.Error as error:
            raise StorageError(f"could not initialize SQLite state: {path}") from error
        except OSError as error:
            raise StorageError(
                f"could not create state directory: {path.parent}"
            ) from error

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def create_session(self, title: str) -> Session:
        session = Session(id=new_id("ses"), title=title, status="active")
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO sessions (id, title, status)
                    VALUES (?, ?, ?)
                    """,
                    (session.id, session.title, session.status),
                )
        except sqlite3.Error as error:
            raise StorageError("could not create session") from error
        return session

    def get_session(self, session_id: str) -> Session | None:
        row = self._connection.execute(
            "SELECT id, title, status FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return None
        return Session(id=row["id"], title=row["title"], status=row["status"])

    def get_or_create_session(
        self,
        *,
        requested_session_id: str | None,
        title: str,
    ) -> Session:
        if requested_session_id is None:
            return self.create_session(title)
        session = self.get_session(requested_session_id)
        if session is not None:
            return session
        session = Session(id=requested_session_id, title=title, status="active")
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO sessions (id, title, status)
                    VALUES (?, ?, ?)
                    """,
                    (session.id, session.title, session.status),
                )
        except sqlite3.Error as error:
            raise StorageError("could not create requested session") from error
        return session

    def start_run(self, session_id: str) -> Run:
        run = Run(id=new_id("run"), session_id=session_id, status="running")
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO runs (id, session_id, status)
                    VALUES (?, ?, ?)
                    """,
                    (run.id, run.session_id, run.status),
                )
        except sqlite3.Error as error:
            raise StorageError("could not start run") from error
        return run

    def add_message(self, session_id: str, run_id: str, message: Message) -> None:
        tool_calls_json = json.dumps(
            [
                {
                    "id": tool_call.id,
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                }
                for tool_call in message.tool_calls
            ],
            sort_keys=True,
        )
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO messages (
                        id, session_id, run_id, role, content, reasoning_content,
                        tool_call_id, tool_calls_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message.id,
                        session_id,
                        run_id,
                        message.role,
                        message.content,
                        message.reasoning_content,
                        message.tool_call_id,
                        tool_calls_json,
                    ),
                )
                self._touch_session(session_id)
        except sqlite3.Error as error:
            raise StorageError("could not persist message") from error

    def load_messages(self, session_id: str) -> tuple[Message, ...]:
        rows = self._connection.execute(
            """
            SELECT id, role, content, reasoning_content, tool_call_id, tool_calls_json
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at, rowid
            """,
            (session_id,),
        ).fetchall()
        return tuple(_message_from_row(row) for row in rows)

    def record_event(self, run_id: str, event: HarnessEvent) -> None:
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO events (run_id, type, payload_json)
                    VALUES (?, ?, ?)
                    """,
                    (
                        run_id,
                        event.type,
                        json.dumps(event.payload, sort_keys=True),
                    ),
                )
        except sqlite3.Error as error:
            raise StorageError("could not persist event") from error

    def record_tool_call(
        self,
        *,
        run_id: str,
        provider_tool_call_id: str,
        name: str,
        arguments_json: str,
    ) -> StoredToolCall:
        stored = StoredToolCall(
            id=new_id("tool"),
            provider_tool_call_id=provider_tool_call_id,
            name=name,
            arguments_json=arguments_json,
            status="running",
            result_text=None,
            error_message=None,
        )
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO tool_calls (
                        id, run_id, provider_tool_call_id, name,
                        arguments_json, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        stored.id,
                        run_id,
                        stored.provider_tool_call_id,
                        stored.name,
                        stored.arguments_json,
                        stored.status,
                    ),
                )
        except sqlite3.Error as error:
            raise StorageError("could not persist tool call") from error
        return stored

    def finish_tool_call(
        self,
        *,
        stored_tool_call_id: str,
        status: str,
        result_text: str | None,
        error_message: str | None,
    ) -> None:
        try:
            with self._connection:
                self._connection.execute(
                    """
                    UPDATE tool_calls
                    SET status = ?, result_text = ?, error_message = ?
                    WHERE id = ?
                    """,
                    (status, result_text, error_message, stored_tool_call_id),
                )
        except sqlite3.Error as error:
            raise StorageError("could not update tool call") from error

    def record_usage(self, run_id: str, usage: ProviderUsage) -> None:
        try:
            with self._connection:
                self._connection.execute(
                    """
                    INSERT INTO provider_usage (
                        run_id, prompt_tokens, completion_tokens, reasoning_tokens,
                        prompt_cache_hit_tokens, prompt_cache_miss_tokens
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(run_id) DO UPDATE SET
                        prompt_tokens = excluded.prompt_tokens,
                        completion_tokens = excluded.completion_tokens,
                        reasoning_tokens = excluded.reasoning_tokens,
                        prompt_cache_hit_tokens = excluded.prompt_cache_hit_tokens,
                        prompt_cache_miss_tokens = excluded.prompt_cache_miss_tokens
                    """,
                    (
                        run_id,
                        usage.prompt_tokens,
                        usage.completion_tokens,
                        usage.reasoning_tokens,
                        usage.prompt_cache_hit_tokens,
                        usage.prompt_cache_miss_tokens,
                    ),
                )
        except sqlite3.Error as error:
            raise StorageError("could not persist provider usage") from error

    def complete_run(self, run_id: str) -> None:
        self._finish_run(run_id, "completed", None, None)

    def fail_run(self, run_id: str, error_code: str, error_message: str) -> None:
        self._finish_run(run_id, "failed", error_code, error_message)

    def cancel_run(self, run_id: str) -> None:
        self._finish_run(run_id, "cancelled", None, None)

    def run_status(self, run_id: str) -> str:
        row = self._connection.execute(
            "SELECT status FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            raise StorageError(f"run not found: {run_id}")
        return cast(str, row["status"])

    def events_for_run(self, run_id: str) -> tuple[HarnessEvent, ...]:
        rows = self._connection.execute(
            "SELECT type, payload_json FROM events WHERE run_id = ? ORDER BY id",
            (run_id,),
        ).fetchall()
        return tuple(
            HarnessEvent(type=row["type"], payload=json.loads(row["payload_json"]))
            for row in rows
        )

    def _finish_run(
        self,
        run_id: str,
        status: str,
        error_code: str | None,
        error_message: str | None,
    ) -> None:
        try:
            with self._connection:
                self._connection.execute(
                    """
                    UPDATE runs
                    SET status = ?,
                        ended_at = CURRENT_TIMESTAMP,
                        error_code = ?,
                        error_message = ?
                    WHERE id = ?
                    """,
                    (status, error_code, error_message, run_id),
                )
        except sqlite3.Error as error:
            raise StorageError("could not finish run") from error

    def _touch_session(self, session_id: str) -> None:
        self._connection.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )

    def _create_schema(self) -> None:
        with self._connection:
            for statement in _SCHEMA:
                self._connection.execute(statement)


def _message_from_row(row: sqlite3.Row) -> Message:
    raw_tool_calls = json.loads(row["tool_calls_json"])
    if not isinstance(raw_tool_calls, list):
        raise StorageError("stored message has invalid tool_calls_json")
    tool_calls = tuple(_tool_call_from_dict(value) for value in raw_tool_calls)
    return Message(
        id=row["id"],
        role=row["role"],
        content=row["content"],
        reasoning_content=row["reasoning_content"],
        tool_call_id=row["tool_call_id"],
        tool_calls=tool_calls,
    )


def _tool_call_from_dict(value: object) -> ToolCall:
    if not isinstance(value, dict):
        raise StorageError("stored tool call is invalid")
    tool_call_id = value.get("id")
    name = value.get("name")
    arguments = value.get("arguments")
    if not isinstance(tool_call_id, str):
        raise StorageError("stored tool call id is invalid")
    if not isinstance(name, str):
        raise StorageError("stored tool call name is invalid")
    if not isinstance(arguments, str):
        raise StorageError("stored tool call arguments are invalid")
    return ToolCall(id=tool_call_id, name=name, arguments=arguments)


_SCHEMA: Iterable[str] = (
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY
    )
    """,
    """
    INSERT OR IGNORE INTO schema_version (version) VALUES (1)
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runs (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL REFERENCES sessions(id),
        status TEXT NOT NULL,
        started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at TEXT,
        error_code TEXT,
        error_message TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL REFERENCES sessions(id),
        run_id TEXT NOT NULL REFERENCES runs(id),
        role TEXT NOT NULL,
        content TEXT,
        reasoning_content TEXT,
        tool_call_id TEXT,
        tool_calls_json TEXT NOT NULL DEFAULT '[]',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tool_calls (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES runs(id),
        provider_tool_call_id TEXT NOT NULL,
        name TEXT NOT NULL,
        arguments_json TEXT NOT NULL,
        result_text TEXT,
        status TEXT NOT NULL,
        error_message TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS provider_usage (
        run_id TEXT PRIMARY KEY REFERENCES runs(id),
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        reasoning_tokens INTEGER,
        prompt_cache_hit_tokens INTEGER,
        prompt_cache_miss_tokens INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL REFERENCES runs(id),
        type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
)
