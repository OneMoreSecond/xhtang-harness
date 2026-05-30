Task ID: 2026-05-30-greenfield

# Gree field setup

## Background

This project is a LLM Agent Harness, requiring show a usable demo in limited time.
I plan to build on Python.

## Goal

setup the project following python-greefield skill.

add new chapters in AGENTS.md to describe the setup.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Python package | Installable project code under `src/xhtang_harness`. | [python-green-field skill: Default Layout] |
| Distribution name | Package published/installed as `xhtang-harness`. | [Decision based on repository directory name] |
| Import package | Python import name `xhtang_harness`. | [Decision based on Python package naming rules] |
| CLI | Command-line entry point for a quick usable demo. | [User task goal: "requiring show a usable demo in limited time"] |
| uv project environment | Checkout-local environment managed by `uv sync` and used through `uv run`. | [uv project guide: https://docs.astral.sh/uv/guides/projects/] |

- The repository contains a Python package skeleton under `src/xhtang_harness/`, a minimal CLI in `src/xhtang_harness/cli.py`, tests in `tests/`, project metadata in `pyproject.toml`, a `.python-version` pin, and setup documentation in `README.md` and `AGENTS.md`. [source: `rg --files`, `pyproject.toml`, `README.md`, `.python-version`]
- Root `AGENTS.md` no longer forbids virtual environments and now should document uv project commands. [source: user instruction, `AGENTS.md`]
- Local tools available include `python3.12` 3.12.9 and `uv` 0.11.16. Development tools should be run from the uv-managed project environment. [source: shell tool checks, user instruction]
- The `python-green-field` skill recommends `src/` layout, `pyproject.toml`, `pytest`, `ruff`, one type checker, and a small installable package. [source: `python-green-field` skill]
- uv documents `uv run` as the project command runner and says it keeps the environment up to date before running the command. [source: uv running commands docs: https://docs.astral.sh/uv/concepts/projects/run/]
- uv creates a project virtual environment and `uv.lock` in the project root when project commands run, so each git worktree gets an isolated local environment. [source: uv project guide: https://docs.astral.sh/uv/guides/projects/]

## Constraint and Assumption

- Preserve the original task text above the separator and keep implementation scope small. [source: `AGENTS.md`]
- Treat this as a private/internal application package, not a package intended for public publishing. [source: task context plus decision]
- Use `xhtang-harness` as the distribution name and `xhtang_harness` as the import package name. [source: repository name]
- Use uv as the canonical project manager because the user explicitly requested the canonical uv solution. [source: user instruction]
- Pin the local project interpreter to Python 3.12 with `.python-version`, while keeping `requires-python = ">=3.12"` in package metadata. [source: uv project guide, `pyproject.toml`]
- Avoid user-wide project installation for normal CLI execution; `uv run xhtang-harness` runs the package script in the current checkout's uv environment. [source: user instruction, uv running commands docs]
- Defer runtime LLM provider integration; the greenfield task is project setup plus a minimal CLI demo. [source: limited task scope]

## Challenges

- A meaningful LLM agent harness needs product decisions not present in the task, so the initial demo should avoid fake provider behavior. [source: task document]
- Installed console scripts are user-wide and can point at the wrong editable checkout when multiple git worktrees exist; uv project commands avoid that by using the current checkout. [source: user instruction, uv running commands docs]

## Decisions

- Create a minimal installable Python package using `src/` layout and Hatchling build backend. [source: `python-green-field` skill]
- Add a small CLI with `argparse` so the repository has an immediate demo surface without speculative architecture. [source: task goal and simplicity constraint]
- Configure dev tooling in `pyproject.toml`: `pytest`, `ruff`, and `mypy`. [source: `python-green-field` skill]
- Add `.python-version` with `3.12` for uv's project interpreter selection. [source: uv project guide]
- Add `uv.lock` for reproducible dependency resolution and document `uv sync`, `uv run xhtang-harness`, and `uv run ...` checks as the canonical workflow. [source: user instruction, uv project guide]
- Remove the custom `bin/xhtang-harness` wrapper because `uv run xhtang-harness` is the narrower canonical interface and still works per checkout/worktree. [source: user instruction, uv running commands docs]
- Do not add pre-commit, CI, docs, examples, or service scaffolding in this task. [source: limited task scope]

## Design

- Add project metadata and tool configuration in `pyproject.toml`.
- Add `src/xhtang_harness/` with `__init__.py`, `__main__.py`, `cli.py`, and `py.typed`.
- Add `.python-version` to pin uv's local interpreter family.
- Expose the CLI through `[project.scripts]` and run it with `uv run xhtang-harness`.
- Add focused tests under `tests/` for the CLI demo and package metadata.
- Add `README.md` with canonical uv setup/test commands.
- Add `.gitignore` for Python caches, local environments, build outputs, coverage files, and secret env files.
- Add an `AGENTS.md` project setup chapter describing package layout and uv commands.

## Todo

- [x] Read task document and root instructions.
- [x] Check local Python and tooling availability.
- [x] Add project skeleton files.
- [x] Generate dependency lockfile.
- [x] Run formatting, lint, tests, and type checks through uv.
- [x] Add a local no-install command entry compatible with git worktrees.
- [x] Update README, AGENTS, and tests for the local command entry.
- [x] Replace the custom local wrapper with canonical uv project commands.
- [x] Add `.python-version` for uv's local interpreter selection.
- [x] Remove pytest's `pythonpath` override so uv-installed package behavior is tested.
- [x] Update task results and append task history.

## Results

- Added a Python 3.12 project skeleton with `.python-version`, `pyproject.toml`, `README.md`, `.gitignore`, `src/xhtang_harness/`, `tests/`, and `uv.lock`. [source: code changes]
- Added a minimal CLI demo available through `uv run xhtang-harness "Show a usable agent harness demo"` without user-wide installation. [source: `pyproject.toml`, `src/xhtang_harness/cli.py`, `README.md`]
- Added `AGENTS.md` project setup chapters for package layout, `uv sync`, uv-run CLI execution, uv-run checks, and `uv lock` maintenance. [source: `AGENTS.md`]
- Removed `bin/xhtang-harness`; the canonical local command is now the project script invoked by uv. [source: user instruction, code changes]
- Removed pytest's `pythonpath = ["src"]` override so `uv run pytest` uses the package installed in the uv project environment. [source: `pyproject.toml`, uv project guide]
- Verified `uv sync` succeeds. [source: shell validation]
- Verified `uv run python --version` uses Python 3.12.9. [source: shell validation]
- Verified `uv run xhtang-harness "Show a usable agent harness demo"` and `uv run python -m xhtang_harness "Show a usable agent harness demo"` succeed. [source: shell validation]
- Verified `uv run pytest` passes with 4 tests. [source: shell validation]
- Verified `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` pass. [source: shell validation]
