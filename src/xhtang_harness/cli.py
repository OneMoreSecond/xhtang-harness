from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import cast

from xhtang_harness import __version__
from xhtang_harness.app import run_harness
from xhtang_harness.config import ConfigOverrides, load_config
from xhtang_harness.errors import HarnessError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xhtang-harness",
        description="Run a local DeepSeek-backed agent harness.",
    )
    parser.add_argument(
        "goal",
        nargs="?",
        help="Initial prompt to pass to the harness. Omit to be prompted.",
    )
    parser.add_argument("--session", help="Session id to continue or create.")
    parser.add_argument(
        "--thinking",
        choices=["enabled", "disabled"],
        help="DeepSeek thinking mode.",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["high", "max"],
        help="DeepSeek reasoning effort when thinking is enabled.",
    )
    stream_group = parser.add_mutually_exclusive_group()
    stream_group.add_argument(
        "--stream",
        dest="stream",
        action="store_true",
        default=None,
        help="Render progress events as they are produced.",
    )
    stream_group.add_argument(
        "--no-stream",
        dest="stream",
        action="store_false",
        help="Render only non-delta status and final output events.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Request JSON output from the provider and render JSON event lines.",
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        help="SQLite state path. Defaults to .xhtang-harness/state.sqlite3.",
    )
    parser.add_argument(
        "--skill-learning",
        choices=["off", "suggest", "auto"],
        help="After a successful run, ask whether to create a reusable skill.",
    )
    parser.add_argument(
        "--skills-path",
        type=Path,
        help="Directory for local skill files. Defaults to .skills.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include local runtime details in status output.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)
    goal = cast(str | None, namespace.goal)
    overrides = ConfigOverrides(
        session=cast(str | None, namespace.session),
        thinking=cast(str | None, namespace.thinking),
        reasoning_effort=cast(str | None, namespace.reasoning_effort),
        stream=cast(bool | None, namespace.stream),
        json_output=cast(bool, namespace.json_output),
        state_path=cast(Path | None, namespace.state_path),
        skill_learning=cast(str | None, namespace.skill_learning),
        skills_path=cast(Path | None, namespace.skills_path),
        debug=cast(bool, namespace.debug),
    )

    try:
        if goal is None:
            goal = _read_initial_goal()
        config = load_config(prompt=goal, overrides=overrides)
        if config.debug and not config.json_output:
            print(f"state_path: {config.state_path}")

        while True:
            last_event_type = None
            run_completed = False
            session_id = config.session
            for event in run_harness(config):
                last_event_type = event.type
                if event.type == "run_started":
                    event_session_id = event.payload.get("session_id")
                    if isinstance(event_session_id, str) and event_session_id.strip():
                        session_id = event_session_id
                if event.type == "run_completed":
                    run_completed = True
                print(_render_event(event, json_output=config.json_output), flush=True)

            if last_event_type == "run_cancelled":
                return 130
            if last_event_type == "run_failed":
                return 1
            if not run_completed:
                return 0

            next_prompt = _read_additional_prompt()
            if next_prompt is None:
                return 0
            config = replace(config, prompt=next_prompt, session=session_id)
    except HarnessError as error:
        print(f"{error.code}: {error.message}", file=sys.stderr)
        return error.exit_code
    except ValueError as error:
        parser.error(str(error))


def _render_event(event: object, *, json_output: bool) -> str:
    from xhtang_harness.events import HarnessEvent

    if not isinstance(event, HarnessEvent):
        raise TypeError("event must be a HarnessEvent")
    if json_output:
        return event.to_json_line()

    payload = event.payload
    if event.type == "run_started":
        return f"run_started: {payload['run_id']} session={payload['session_id']}"
    if event.type == "provider_request_started":
        return (
            f"provider_request_started: model={payload['model']} "
            f"thinking={payload['thinking_mode']}"
        )
    if event.type == "answer_delta":
        return f"answer_delta: {payload['text']}"
    if event.type == "tool_call_started":
        command = payload.get("command")
        if isinstance(command, str):
            return (
                f"tool_call_started: {payload['name']} "
                f"command={json.dumps(command, ensure_ascii=False)}"
            )
        return f"tool_call_started: {payload['name']}"
    if event.type == "tool_call_finished":
        return f"tool_call_finished: {payload['status']} {payload['summary']}"
    if event.type == "retry_scheduled":
        return (
            f"retry_scheduled: attempt={payload['attempt']} "
            f"delay={payload['delay_seconds']}s"
        )
    if event.type == "run_completed":
        return f"run_completed: {payload['run_id']}"
    if event.type == "run_failed":
        return f"run_failed: {payload['message']}"
    if event.type == "run_cancelled":
        return f"run_cancelled: {payload['run_id']}"
    if event.type == "message_recorded":
        return f"message_recorded: {payload['role']} {payload['message_id']}"
    if event.type == "skill_context_loaded":
        return f"skill_context_loaded: {payload['skill_count']} local skill(s)"
    if event.type == "skill_learning_started":
        return "skill_learning_started: thinking whether to create a skill"
    if event.type == "skill_learning_skipped":
        return f"skill_learning_skipped: {payload['reason']}"
    if event.type == "skill_proposed":
        return f"skill_proposed: {payload['skill_name']} {payload['reason']}"
    if event.type == "skill_write_started":
        return f"skill_write_started: {payload['skill_name']}"
    if event.type == "skill_written":
        return f"skill_written: {payload['skill_name']} {payload['target_path']}"
    if event.type == "skill_learning_failed":
        return f"skill_learning_failed: {payload['message']}"
    return event.to_json_line()


def _read_additional_prompt() -> str | None:
    if not sys.stdin.isatty():
        return None

    print("additional prompt (blank to exit): ", end="", file=sys.stderr, flush=True)
    raw_prompt = sys.stdin.readline()
    if raw_prompt == "":
        return None

    prompt = raw_prompt.strip()
    if not prompt:
        return None
    return prompt


def _read_initial_goal() -> str:
    print("initial goal: ", end="", file=sys.stderr, flush=True)
    return sys.stdin.readline().strip()
