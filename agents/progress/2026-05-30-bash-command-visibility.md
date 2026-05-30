Task ID: 2026-05-30-bash-command-visibility

# Bash Command Visibility

## Original Request

current bash tool call won't print the called bash command. please print it even the debug mode is not enabled.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Bash tool | Built-in tool named `bash` that runs `/bin/bash -lc` with captured output and timeout. | [source: `src/xhtang_harness/tools/builtin.py`] |
| Tool-call event | Runtime event emitted before and after a model-requested tool execution. | [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/events.py`] |
| Normal CLI output | Human-readable event rendering used when `--json` is not set. | [source: `src/xhtang_harness/cli.py`] |

- `AgentLoop._execute_tool_call` already has access to the provider tool call name and JSON arguments before execution. [source: `src/xhtang_harness/agent_loop.py`]
- `tool_call_started` currently includes only `tool_call_id` and `name`, so normal output prints only `tool_call_started: bash`. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`]
- Bash tool arguments use a required string field named `command`. [source: `src/xhtang_harness/tools/builtin.py`]
- JSON output mode serializes the event payload directly, so adding the command to the event payload also exposes it to JSON event consumers. [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/events.py`]

## Constraint and Assumption

- The user wants the bash command printed even when `--debug` is not enabled. [source: user request]
- The command should be printed when the model requests the bash tool, before tool execution finishes. [source: design decision]
- This change should not alter how the bash tool executes commands. [source: user request, `src/xhtang_harness/tools/builtin.py`]
- Invalid or non-object tool arguments should not break event rendering; execution will still fail through the existing `ToolExecutor` validation path. [source: `src/xhtang_harness/tools/executor.py`, design decision]

## Challenges

- Tool-call arguments are JSON strings from the provider, so command extraction must be tolerant of malformed JSON. [source: `src/xhtang_harness/providers/deepseek.py`, `src/xhtang_harness/tools/executor.py`]
- Only bash has a user-meaningful shell command field; other tools should keep the existing compact event output. [source: `src/xhtang_harness/tools/builtin.py`, design decision]

## Decisions

- Add `command` to the `tool_call_started` event payload only for bash tool calls with a string `command` argument. [source: design decision]
- Render `tool_call_started: bash command=<command>` in normal CLI output when the payload contains `command`. [source: user request, design decision]
- Preserve existing JSON mode by relying on `event.to_json_line()`, which will include the new payload field automatically. [source: `src/xhtang_harness/cli.py`]

## Design

Implement a small helper in `agent_loop.py` that builds the `tool_call_started` payload from `DeepSeekToolCall`. It parses `arguments` as JSON, adds `command` for bash only when the value is a string, and otherwise returns the existing payload shape. [source: design decision]

Update CLI rendering for `tool_call_started` to include `command=<value>` when present. [source: user request, `src/xhtang_harness/cli.py`]

Add tests at the event and CLI-rendering layers. [source: `tests/test_agent_loop.py`, `tests/test_cli.py`]

## Todo

- [x] Inspect current tool event and CLI rendering code. [source: task work]
- [x] Create task progress and history files. [source: task work]
- [x] Add bash command to `tool_call_started` event payload. [source: user request]
- [x] Render bash command in normal CLI output. [source: user request]
- [x] Add tests. [source: `AGENTS.md`]
- [x] Run checks and update results. [source: `AGENTS.md`]

## Results

Updated `AgentLoop` so `tool_call_started` events include `command` for bash tool calls when the provider arguments contain a string `command`. Updated normal CLI rendering so it prints `tool_call_started: bash command="<command>"` even when `--debug` is not enabled. JSON mode includes the same command through the event payload. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`]

Added tests for the bash command event payload and non-debug CLI rendering. Updated `README.md` and `USAGE.md` to document the new behavior. [source: `tests/test_agent_loop.py`, `tests/test_cli.py`, `README.md`, `USAGE.md`]

Validation results: focused `uv run pytest tests/test_agent_loop.py tests/test_cli.py` passed, full `uv run pytest` passed with 55 tests, `uv run ruff format --check .` passed, and `uv run mypy src` passed. `uv run ruff check .` failed only on existing tracked file `examples/fib30.py` for `B905 zip() without strict=`, which this task did not touch. Local validation caches were removed after the run. [source: command output]
