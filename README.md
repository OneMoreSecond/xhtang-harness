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
uv run xhtang-harness --no-stream --state-path .xhtang-harness/state.sqlite3 "hello"
uv run xhtang-harness --debug "hello"
```

The default SQLite state is worktree-local at `.xhtang-harness/state.sqlite3`.
Use `--state-path` or `XHTANG_HARNESS_STATE_PATH` only when you want to share
state explicitly.

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
