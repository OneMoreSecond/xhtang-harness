# Contributing

This repository contains a Python 3.12 package for a local DeepSeek-backed agent
harness. This document is for developers working on the codebase. [source:
`pyproject.toml`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/app.py`]

## Requirements

| Requirement | Detail | Source |
| --- | --- | --- |
| `uv` | Used for environment setup, local commands, and dependency locking. | `pyproject.toml`, `uv.lock` |
| Python 3.12 | Selected by uv from `.python-version`; package metadata requires Python 3.12 or newer. | `.python-version`, `pyproject.toml` |
| `DEEPSEEK_API_KEY` | Required only for live provider-backed runs. | `src/xhtang_harness/config.py`, `src/xhtang_harness/app.py` |

## Setup

Create or update the local uv project environment:

```bash
uv sync
```

For live provider checks, set a DeepSeek API key in the shell:

```bash
export DEEPSEEK_API_KEY="..."
```

## Developer Run Commands

Run a simple provider-backed prompt:

```bash
uv run xhtang-harness "Reply with one short sentence: hello from xhtang-harness."
```

Run with explicit tool use:

```bash
uv run xhtang-harness "Use the get_current_time tool, then tell me the UTC time."
uv run xhtang-harness "Use the bash tool to run: pwd"
```

Run with common debug/config options:

```bash
uv run xhtang-harness --thinking enabled --reasoning-effort high "Use the current time tool."
uv run xhtang-harness --state-path .xhtang-harness/state.sqlite3 "hello"
uv run xhtang-harness --debug "hello"
uv run xhtang-harness --skill-learning suggest "Capture the reusable workflow."
```

## Directory Structure

| Path | Purpose | Source |
| --- | --- | --- |
| `.agents/skills/` | Local agent skills used while developing this repository. | `find . -maxdepth 3 -type d` |
| `agents/` | Task notes, progress records, and implementation history for agent work. | `find . -maxdepth 3 -type f` |
| `doc/` | Design notes for external interfaces, module responsibilities, MVP scope, storage, runtime reliability, and UX expectations. | `find . -maxdepth 3 -type f` |
| `examples/` | Small example files, currently including a Fibonacci script example. | `examples/fib30.py` |
| `src/xhtang_harness/` | Application package code for the CLI, config, app service, agent loop, events, provider, storage, skills, and tools. | `find src/xhtang_harness -maxdepth 3 -type f` |
| `tests/` | Test coverage for the CLI, app flow, agent loop, config, provider layer, storage, skills, and tools. | `find tests -maxdepth 3 -type f` |
| `USAGE.md` | Application-user guide for running the CLI. | `USAGE.md` |
| `CONTRIBUTION.md` | Developer setup, structure, and contribution workflow. | `CONTRIBUTION.md` |
| `dev-env-snapshot.md` | Captured development environment snapshot. | `dev-env-snapshot.md` |
| `pyproject.toml` | Python package metadata, script entry point, dependencies, and tool configuration. | `pyproject.toml` |
| `uv.lock` | uv dependency lockfile. | `uv.lock` |

Generated local directories such as `.venv/`, caches, `.xhtang-harness/`, and
`.skills/` are not part of the source layout. `.venv/` and common caches are
ignored by `.gitignore`; runtime state and generated skills may appear locally
when you run the harness. [source: `.gitignore`, `src/xhtang_harness/config.py`]

## Implementation Map

| Area | Files | Purpose |
| --- | --- | --- |
| CLI | `src/xhtang_harness/cli.py`, `src/xhtang_harness/__main__.py` | Argument parsing, event rendering, exit codes, and module entry. |
| Config | `src/xhtang_harness/config.py` | CLI/env/TOML configuration loading and validation. |
| App orchestration | `src/xhtang_harness/app.py`, `src/xhtang_harness/agent_loop.py` | Provider-backed harness run flow, retries, tools, persistence, and skill learning. |
| Events and errors | `src/xhtang_harness/events.py`, `src/xhtang_harness/errors.py` | User-visible event objects and typed harness errors. |
| Provider layer | `src/xhtang_harness/providers/` | DeepSeek/OpenAI-compatible provider integration. |
| Storage | `src/xhtang_harness/storage/` | SQLite-backed sessions, messages, events, tool calls, and usage state. |
| Tools | `src/xhtang_harness/tools/` | Tool registry, executor, current-time tool, and bash tool. |
| Skills | `src/xhtang_harness/skills.py` | Local skill loading and generated skill validation/writes. |
| Tests | `tests/` | Unit and integration coverage by module area. |

## Local State And Skills

Default local paths are worktree-local:

| Path | Purpose | Source |
| --- | --- | --- |
| `.xhtang-harness/config.toml` | Optional local config file read from the current worktree. | `src/xhtang_harness/config.py` |
| `.xhtang-harness/state.sqlite3` | Default SQLite state path for sessions, runs, messages, events, tools, and usage. | `src/xhtang_harness/config.py`, `src/xhtang_harness/storage/sqlite.py` |
| `.skills/<skill-name>/SKILL.md` | Default local skill path loaded when a prompt includes the skill name or exact description. | `src/xhtang_harness/config.py`, `src/xhtang_harness/skills.py` |

Use `--state-path`, `XHTANG_HARNESS_STATE_PATH`, `--skills-path`, or
`XHTANG_HARNESS_SKILLS_PATH` only when you intentionally want a shared or custom
path. [source: `src/xhtang_harness/config.py`]

## Built-In Tools

| Tool | Purpose | Source |
| --- | --- | --- |
| `get_current_time` | Returns the current UTC time as an ISO-8601 timestamp. | `src/xhtang_harness/tools/builtin.py` |
| `bash` | Runs `/bin/bash -lc` with captured stdout, stderr, exit code, optional `cwd`, and a bounded timeout. | `src/xhtang_harness/tools/builtin.py` |

The `bash` tool should be used for read-only inspection unless the user
explicitly asks for local file changes. [source:
`src/xhtang_harness/tools/builtin.py`]

## Checks

Run local checks through uv:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

Refresh the lockfile when dependencies change:

```bash
uv lock
```
