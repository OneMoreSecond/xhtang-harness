# xhtang-harness

Small Python foundation for an LLM agent harness demo.

## Requirements

- `uv`
- Python 3.12, selected by uv from `.python-version`

## Setup

Create or update the local uv project environment:

```bash
uv sync
```

## Demo

Run the CLI demo from this checkout or git worktree:

```bash
uv run xhtang-harness "Show a usable agent harness demo"
```

Or run it as a module:

```bash
uv run python -m xhtang_harness "Show a usable agent harness demo"
```

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
