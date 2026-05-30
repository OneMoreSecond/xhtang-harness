Task ID: 2026-05-30-init-design

# Initial design

previous work: 2026-05-30-greenfield.md

## Background

Now we are plan for module design and implementation.

## Goal

Write multiple markdown design docs to doc/, including but not limited to:

- UX expectation: it should be responsive and to avoid long-time stuck in which the user canno input text.
- module responsibilities
- persistent data storage
- other topics you think important.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Harness | The local Python application that mediates between user input, model provider calls, tools, storage, and streamed output. | [source: user task, `agents/2026-05-30-greenfield.md`] |
| Worktree-local CLI | `./bin/xhtang-harness`, a command entry that runs the current checkout without user-wide package installation. | [source: `bin/xhtang-harness`, `agents/2026-05-30-greenfield.md`] |
| DeepSeek provider | DeepSeek V4 Pro API integration planned as the main LLM backend. | [source: `agents/2026-05-30-deepseek-api.md`, `.agents/skills/deepseek-api/SKILL.md`] |
| Streaming UX | A user experience where model output and status events appear incrementally while the request is still running. | [source: user task, `.agents/skills/deepseek-api/SKILL.md`] |
| Persistent store | Local durable storage for sessions, messages, tool calls, provider metadata, and run status. | [source: user task, design decision] |

- Existing code is a Python 3.12 package skeleton with a minimal CLI demo and worktree-local command entry. [source: `src/xhtang_harness/cli.py`, `bin/xhtang-harness`, `pyproject.toml`]
- The repository currently has an empty `doc/` directory, so this task should create initial design docs rather than update existing design docs. [source: `find doc -maxdepth 3 -type f`]
- Root project rules require direct `python3.12` commands and no virtual environment. [source: `AGENTS.md`]
- DeepSeek guidance already exists as a repo-local skill and should inform provider-facing design, especially streaming, `reasoning_content`, tool calls, and cache telemetry. [source: `.agents/skills/deepseek-api/SKILL.md`]

## Constraint and Assumption

- Preserve the original task text above the separator. [source: `AGENTS.md`]
- Keep this as a design-only task; do not implement runtime modules yet. [source: user task wording]
- Use multiple focused Markdown files under `doc/` instead of one large document. [source: user task]
- Design for a fast demo while leaving interfaces clear enough for later implementation. [source: user task, `agents/2026-05-30-greenfield.md`]
- Prefer simple Python standard-library choices unless a dependency removes real implementation complexity. [source: `AGENTS.md`, design decision]

## Challenges

- The UX requirement explicitly calls out avoiding long stuck states where the user cannot input text, which affects runtime architecture, not just UI copy. [source: user task]
- Thinking-mode provider calls can have long-running model/tool loops; the design needs event streaming, cancellation, and durable run status. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Persistent storage must be useful for resumed sessions without overbuilding a multi-user database too early. [source: user task, simplicity constraint in `AGENTS.md`]

## Decisions

- Create four initial design docs: UX expectations, module responsibilities, persistent data storage, and runtime flow/reliability. [source: user task, design decision]
- Use SQLite as the initial persistent store because Python includes `sqlite3`, the app is local-first, and session/message data benefits from transactions and queries. [source: Python standard library knowledge, design decision]
- Model runtime output as events so CLI/TUI/web frontends can stay responsive and avoid blocking input while provider calls run. [source: user UX requirement, design decision]
- Keep model-provider specifics behind a provider module so DeepSeek can be the default without leaking API details across the app. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]

## Design

- `doc/ux-expectations.md`: define user-facing responsiveness expectations and interaction states.
- `doc/module-responsibilities.md`: define module boundaries and ownership.
- `doc/persistent-data-storage.md`: define storage scope, SQLite schema draft, and retention/privacy expectations.
- `doc/runtime-flow-and-reliability.md`: define the streaming run loop, cancellation, tool calls, retries, and observability.

## Todo

- [x] Read task document and previous greenfield design context.
- [x] Inspect current code scaffold and DeepSeek skill.
- [x] Normalize task document and create side history.
- [x] Create design docs under `doc/`.
- [x] Review Markdown files touched/read for outdated content.
- [x] Run available checks.
- [x] Update results and task history.

## Results

- Created `doc/ux-expectations.md` to define responsive input, streaming progress, cancellation, tool status, failure recovery, and first-demo UX scope. [source: `doc/ux-expectations.md`]
- Created `doc/module-responsibilities.md` to define proposed module boundaries for CLI, app coordination, conversation models, agent loop, DeepSeek provider, tools, storage, config, and telemetry. [source: `doc/module-responsibilities.md`]
- Created `doc/persistent-data-storage.md` to define SQLite as the first local store, storage path policy, schema draft, write policy, and privacy/retention rules. [source: `doc/persistent-data-storage.md`]
- Created `doc/runtime-flow-and-reliability.md` to define run flow, event streaming, cancellation, retry policy, and DeepSeek-specific state handling. [source: `doc/runtime-flow-and-reliability.md`]
- Reviewed Markdown files read or touched in this task and found no outdated content requiring removal. [source: manual review of `README.md`, `agents/2026-05-30-greenfield.md`, `.agents/skills/deepseek-api/SKILL.md`, and new `doc/` files]
- Verified `PYTHONDONTWRITEBYTECODE=1 python3.12 -m pytest -p no:cacheprovider` passes with 5 tests. [source: shell validation]
- Verified `python3.12 -m ruff check --no-cache .` and `python3.12 -m ruff format --check --no-cache .` pass. [source: shell validation]
- `python3.12 -m mypy src` was attempted but could not run because `mypy` is not installed in the current `python3.12` environment. [source: shell validation]
