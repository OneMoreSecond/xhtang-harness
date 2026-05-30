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

- The repository currently contains only `AGENTS.md`, `agents/2026-05-30-greenfield.md`, and empty/non-code directories; no existing Python project layout or dependency convention exists. [source: `rg --files`, `ls`]
- Root `AGENTS.md` requires using `python3.12` directly and never creating virtual environments. [source: `AGENTS.md`]
- Local tools available: `python3.12` 3.12.9, `uv` 0.11.16, `pytest` 8.3.5, and `ruff` 0.11.4. `mypy` is not installed for `python3.12`. [source: shell tool checks]
- The `python-green-field` skill recommends `src/` layout, `pyproject.toml`, `pytest`, `ruff`, one type checker, and a small installable package. [source: `python-green-field` skill]

## Constraint and Assumption

- Preserve the original task text above the separator and keep implementation scope small. [source: `AGENTS.md`]
- Do not create a virtual environment; validation commands must use `python3.12` directly. [source: `AGENTS.md`]
- Treat this as a private/internal application package, not a package intended for public publishing. [source: task context plus decision]
- Use `xhtang-harness` as the distribution name and `xhtang_harness` as the import package name. [source: repository name]
- Choose `uv` for lockfile maintenance because it is installed and is the skill's default modern choice for new internal packages, but avoid `uv sync` and `uv pip install --user` because the former creates `.venv` and the latter is unsupported by this `uv` version. [source: shell tool checks, `uv pip install --user --dry-run`, `python-green-field` skill, `AGENTS.md`]
- Use `python3.12 -m pip install --user` for optional local installation because root `AGENTS.md` requires direct Python use and no virtual environment. [source: `AGENTS.md`, `python3.12 -m pip install --help`]
- Defer runtime LLM provider integration; the greenfield task is project setup plus a minimal CLI demo. [source: limited task scope]

## Challenges

- The greenfield skill prefers package-manager workflows, while root `AGENTS.md` forbids virtual environments. [source: `python-green-field` skill, `AGENTS.md`]
- A meaningful LLM agent harness needs product decisions not present in the task, so the initial demo should avoid fake provider behavior. [source: task document]
- `mypy` is selected for static typing but is not available locally yet. [source: shell tool check]

## Decisions

- Create a minimal installable Python package using `src/` layout and Hatchling build backend. [source: `python-green-field` skill]
- Add a small CLI with `argparse` so the repository has an immediate demo surface without speculative architecture. [source: task goal and simplicity constraint]
- Configure dev tooling in `pyproject.toml`: `pytest`, `ruff`, and `mypy`. [source: `python-green-field` skill]
- Add `uv.lock` for reproducible dependency resolution but document direct `python3.12` commands for local execution and installation. [source: `uv` availability and root `AGENTS.md`]
- Do not add pre-commit, CI, docs, examples, or service scaffolding in this task. [source: limited task scope]

## Design

- Add project metadata and tool configuration in `pyproject.toml`.
- Add `src/xhtang_harness/` with `__init__.py`, `__main__.py`, `cli.py`, and `py.typed`.
- Add focused tests under `tests/` for the CLI demo and package metadata.
- Add `README.md` with supported Python version and canonical setup/test commands.
- Add `.gitignore` for Python caches, local environments, build outputs, coverage files, and secret env files.
- Add an `AGENTS.md` project setup chapter describing package layout and direct Python commands.

## Todo

- [x] Read task document and root instructions.
- [x] Check local Python and tooling availability.
- [x] Add project skeleton files.
- [x] Generate dependency lockfile without creating a virtual environment.
- [x] Run formatting, lint, tests, and available static checks.
- [x] Update task results and append task history.

## Results

- Added a Python 3.12 project skeleton with `pyproject.toml`, `README.md`, `.gitignore`, `src/xhtang_harness/`, `tests/`, and `uv.lock`. [source: code changes]
- Added a minimal CLI demo available as `xhtang-harness` after installation or as `python3.12 -m xhtang_harness` when installed. [source: `src/xhtang_harness/cli.py`, `README.md`]
- Added `AGENTS.md` project setup chapters for package layout, direct Python checks, pip user installation, and `uv lock` maintenance. [source: `AGENTS.md`]
- Verified `uv lock --check --python python3.12 --no-python-downloads` succeeds and did not create `.venv`. [source: shell validation]
- Verified `python3.12 -m pytest` passes with 4 tests. [source: shell validation]
- Verified `python3.12 -m ruff check .` and `python3.12 -m ruff format --check .` pass. [source: shell validation]
- Verified the demo with `PYTHONPATH=src python3.12 -m xhtang_harness "Show a usable agent harness demo"`. [source: shell validation]
- `python3.12 -m mypy src` is configured but was not runnable because `mypy` is not installed in the current `python3.12` environment. [source: shell validation]
