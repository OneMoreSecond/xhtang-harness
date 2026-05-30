# xhtang-harness

Small Python foundation for a local DeepSeek-backed agent harness.

## Requirements

- `uv`
- Python 3.12, selected by uv from `.python-version`

## Setup

Create or update the local uv project environment:

```bash
uv sync
```

## MVP Run

Set a DeepSeek API key for real provider calls:

```bash
export DEEPSEEK_API_KEY="..."
```

Run the CLI from this checkout or git worktree:

```bash
uv run xhtang-harness "Show a usable agent harness demo"
```

Or run it as a module:

```bash
uv run python -m xhtang_harness "Show a usable agent harness demo"
```

Useful options:

```bash
uv run xhtang-harness --thinking enabled --reasoning-effort high "Use the current time tool."
uv run xhtang-harness "Use the bash tool to run: pwd"
uv run xhtang-harness --no-stream --state-path .xhtang-harness/state.sqlite3 "hello"
uv run xhtang-harness --debug "hello"
uv run xhtang-harness --skill-learning suggest "Capture the reusable workflow."
```

The default SQLite state is worktree-local at `.xhtang-harness/state.sqlite3`.
Use `--state-path` or `XHTANG_HARNESS_STATE_PATH` only when you want to share
state explicitly.

Local skills live under `.skills/<skill-name>/SKILL.md`. If a prompt includes a
skill name or exact description, the harness loads that skill body as a system
instruction. `--skill-learning suggest` asks the provider whether the completed
task deserves a new skill; `--skill-learning auto` writes validated skills to
`.skills/`.

Built-in tools exposed to the model:

- `get_current_time`: returns the current UTC time.
- `bash`: runs a local `/bin/bash -lc` command with captured stdout, stderr,
  exit code, and a bounded timeout.

## Directory Structure

| Path | Purpose | Source |
| --- | --- | --- |
| `.agents/skills/` | Local agent skills used while developing this repository. | `find . -maxdepth 3 -type d` |
| `agents/` | Task notes, progress records, and implementation history for agent work. | `find . -maxdepth 3 -type f` |
| `doc/` | Design notes for external interfaces, module responsibilities, MVP scope, storage, runtime reliability, and UX expectations. | `find . -maxdepth 3 -type f` |
| `examples/` | Small example outputs, currently including a Fibonacci script example. | `find examples -maxdepth 2 -type f` |
| `src/xhtang_harness/` | Application package code for the CLI, agent loop, config, events, telemetry, providers, storage, and tools. | `find . -maxdepth 3 -type f` |
| `tests/` | Test coverage for the CLI, app flow, agent loop, config, events, provider layer, storage, and tools. | `find . -maxdepth 3 -type f` |
| `README.md` | Project overview, setup, run commands, directory summary, and checks. | `README.md` |
| `USAGE.md` | End-user usage guide for running the CLI. | `USAGE.md` |
| `dev-env-snapshot.md` | Captured development environment snapshot. | `dev-env-snapshot.md` |
| `pyproject.toml` | Python package metadata, script entry point, dependencies, and tool configuration. | `pyproject.toml` |
| `uv.lock` | uv dependency lockfile. | `uv.lock` |

Generated local directories such as `.venv/`, caches, and runtime state are not
part of the source layout. [source: `.gitignore`, `git status --short --ignored`]

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
