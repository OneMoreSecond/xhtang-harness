# xhtang-harness

Small Python foundation for an LLM agent harness demo.

## Requirements

- Python 3.12
- `uv` for dependency resolution and lockfile maintenance

This repository follows the local team rule in `AGENTS.md`: use `python3.12`
directly and do not create a virtual environment.

## Setup

Local demo commands do not require installing the package into the user Python
environment.

```bash
./bin/xhtang-harness "Show a usable agent harness demo"
```

Install development tools when they are not already available:

```bash
python3.12 -m pip install --user "pytest>=8.3" "ruff>=0.11" "mypy>=1.15"
```

Refresh the dependency lockfile without creating a virtual environment:

```bash
uv lock --python python3.12 --no-python-downloads
```

## Demo

Run the worktree-local CLI demo:

```bash
./bin/xhtang-harness "Show a usable agent harness demo"
```

Or run it as a module from the checkout:

```bash
PYTHONPATH=src python3.12 -m xhtang_harness "Show a usable agent harness demo"
```

## Checks

```bash
python3.12 -m pytest
python3.12 -m ruff check .
python3.12 -m ruff format --check .
python3.12 -m mypy src
```
