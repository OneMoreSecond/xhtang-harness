# xhtang-harness

Small Python foundation for a local DeepSeek-backed agent harness. [source: `pyproject.toml`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/app.py`]

## Source Labels

| Label | Source |
| --- | --- |
| CLI | `src/xhtang_harness/cli.py` |
| Config | `src/xhtang_harness/config.py` |
| App | `src/xhtang_harness/app.py` |
| Agent loop | `src/xhtang_harness/agent_loop.py` |
| Tools | `src/xhtang_harness/tools/builtin.py` |
| Skills | `src/xhtang_harness/skills.py` |
| Storage | `src/xhtang_harness/storage/sqlite.py` |
| Project | `pyproject.toml`, `.python-version` |
| DeepSeek | `.agents/skills/deepseek-api/SKILL.md` |

## Requirements

| Requirement | Detail | Source |
| --- | --- | --- |
| `uv` | Used for environment setup and local commands. | [source: Project] |
| Python 3.12 | Selected by uv from `.python-version`. | [source: Project] |
| `DEEPSEEK_API_KEY` | Required for real provider-backed runs. | [source: App, Config] |

## Setup

Create or update the local uv project environment: [source: Project]

```bash
uv sync
```

Set a DeepSeek API key before running provider-backed prompts: [source: App, Config, DeepSeek]

```bash
export DEEPSEEK_API_KEY="..."
```

## Quick Start

Run a simple prompt from this checkout or git worktree: [source: CLI, App]

```bash
uv run xhtang-harness "Reply with one short sentence: hello from xhtang-harness."
```

Run the package as a module: [source: Project]

```bash
uv run python -m xhtang_harness "Reply with one short sentence: hello from xhtang-harness."
```

Use an explicit tool request when you want local tool use: [source: Tools, Agent loop]

```bash
uv run xhtang-harness "Use the get_current_time tool, then tell me the UTC time."
uv run xhtang-harness "Use the bash tool to run: pwd"
```

Useful options: [source: CLI, Config]

```bash
uv run xhtang-harness --thinking enabled --reasoning-effort high "Use the current time tool."
uv run xhtang-harness --state-path .xhtang-harness/state.sqlite3 "hello"
uv run xhtang-harness --debug "hello"
uv run xhtang-harness --skill-learning suggest "Capture the reusable workflow."
```

## State And Skills

| Path | Purpose | Source |
| --- | --- | --- |
| `.xhtang-harness/config.toml` | Optional local config file read from the current worktree. | [source: Config] |
| `.xhtang-harness/state.sqlite3` | Default SQLite state path for sessions, runs, messages, events, tools, and usage. | [source: Config, Storage] |
| `.skills/<skill-name>/SKILL.md` | Default local skill path loaded when a prompt includes the skill name or exact description. | [source: Config, Skills] |

Default state and skill paths are worktree-local. Use `--state-path`, `XHTANG_HARNESS_STATE_PATH`, `--skills-path`, or `XHTANG_HARNESS_SKILLS_PATH` only when you want explicit sharing or a custom location. [source: Config]

`--skill-learning suggest` asks the provider whether a completed successful run deserves a reusable skill and prints the proposal without writing skill files. `--skill-learning auto` writes validated skills under `.skills/`. [source: Agent loop, Skills]

## Built-In Tools

| Tool | Purpose | Source |
| --- | --- | --- |
| `get_current_time` | Returns the current UTC time as an ISO-8601 timestamp. | [source: Tools] |
| `bash` | Runs `/bin/bash -lc` with captured stdout, stderr, exit code, optional `cwd`, and a bounded timeout. | [source: Tools] |

The `bash` tool should be used for read-only inspection unless the user explicitly asks for local file changes. [source: Tools]

## Directory Structure

| Path | Purpose | Source |
| --- | --- | --- |
| `.agents/skills/` | Local agent skills used while developing this repository. | [source: DeepSeek] |
| `agents/` | Task notes, progress records, and implementation history for agent work. | [source: `agents/`] |
| `doc/` | Design notes for external interfaces, module responsibilities, MVP scope, storage, runtime reliability, and UX expectations. | [source: `doc/`] |
| `examples/` | Small example files, currently including a Fibonacci script example. | [source: `examples/fib30.py`] |
| `src/xhtang_harness/` | Application package code for the CLI, config, app service, agent loop, events, provider, storage, skills, and tools. | [source: `src/xhtang_harness/`] |
| `tests/` | Test coverage for the CLI, app flow, agent loop, config, provider layer, storage, skills, and tools. | [source: `tests/`] |
| `USAGE.md` | End-user usage guide for running the CLI. | [source: `USAGE.md`] |
| `pyproject.toml` | Python package metadata, script entry point, dependencies, and tool configuration. | [source: Project] |
| `uv.lock` | uv dependency lockfile. | [source: `uv.lock`] |

Generated local directories such as `.venv/`, caches, `.xhtang-harness/`, and `.skills/` are not part of the source layout. `.venv/` and common caches are ignored by `.gitignore`; runtime state and generated skills may appear locally when you run the harness. [source: `.gitignore`, Config, Skills, Storage]

## Checks

Run local checks through uv: [source: Project]

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
