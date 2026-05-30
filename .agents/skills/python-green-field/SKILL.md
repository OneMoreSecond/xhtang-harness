---
name: python-green-field
description: 'Set up brand new Python projects with a clean directory layout, pyproject.toml, src package layout, dependency groups, test/lint/type-check tooling, and reproducible project commands.'
metadata:
  short-description: Start clean Python projects
---

# Python Green Field

Use this skill when creating or reviewing a brand new Python project layout and toolchain. Optimize for a small, installable project that is easy to test, package, and maintain.

## Required Decisions

Collect or state these before writing files:

- Project kind: library, CLI, service, script collection, or research project.
- Import package name and distribution name; make differences explicit.
- Minimum Python version and deployment/runtime target.
- Packaging intent: private app, internal package, or publishable package.
- Package manager. If the repo has no standard, show the choices in "Package Manager Choice" and ask the user to choose based on the project scenario before writing lockfiles or tool-specific config.

## Default Layout

Use this shape for installable code:

```text
.
├── pyproject.toml
├── README.md
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── py.typed
├── tests/
│   └── test_package_name.py
└── .gitignore
```

Add only what the project immediately needs:

- `src/package_name/__main__.py` for `python -m package_name`.
- `src/package_name/cli.py` plus `[project.scripts]` for a CLI.
- `docs/` only when documentation is part of the deliverable.
- `scripts/` only for non-package maintenance scripts.
- `examples/` only when examples are tested or intentionally maintained.

## Toolchain Baseline

Prefer one project metadata file:

- Put package metadata, Python requirement, runtime dependencies, dependency groups, and tool config in `pyproject.toml`.
- Use `[dependency-groups]` for development-only tooling such as tests, lint, type checking, and docs.
- Use `[project.optional-dependencies]` only for installable runtime features users can request.
- Keep `requirements.txt` only for legacy deployment targets that require it.

## Package Manager Choice

Do not mix lockfile managers. If the user has not chosen and there is no repo standard, present this short choice list:

| Choice | Use when | Main files |
| --- | --- | --- |
| `uv` | Default for new applications, CLIs, internal packages, and script collections that need fast installs, lockfiles, `pyproject.toml`, and simple `uv run` commands. | `pyproject.toml`, `uv.lock` |
| `Poetry` | The team already uses Poetry, or the project wants Poetry's packaging/publishing workflow and lockfile conventions. | `pyproject.toml`, `poetry.lock` |
| `PDM` | The project wants a standards-oriented workflow around PEP 621 metadata, dependency groups, and `pdm.lock`. | `pyproject.toml`, `pdm.lock` |
| `Hatch` | The project is mostly a package and benefits from Hatch environments, build config, versioning, or environment matrices. | `pyproject.toml` |
| `pip` + `venv` + optional lock tooling | Enterprise or legacy environments disallow newer project managers, or deployment already depends on requirements files. | `requirements*.txt`, optional lock output |

Default tools:

- Project/dependency runner: ask for a package manager choice if not already fixed; default to `uv` only when the user wants the simplest modern setup.
- Test runner: `pytest`.
- Lint and format: `ruff`.
- Static typing: `mypy` or `pyright`; choose one unless the repo already uses both.
- Build backend: keep the backend simple, commonly `hatchling` for pure Python packages unless repo conventions say otherwise.

## Linting and Static Analysis

Choose tools by concern; do not stack overlapping tools unless the repo already does:

- Format and lint: default to Ruff for formatting, import sorting, and common lint rules. Configure it in `pyproject.toml`.
- Type checking: choose `mypy` when the project values broad Python ecosystem convention and gradual strictness; choose `pyright` when the team wants fast editor-aligned type analysis or already uses Pylance/Pyright.
- Security static analysis: add `bandit` only for services, CLIs, automation, or libraries that handle files, subprocesses, credentials, network input, or untrusted data.
- Dependency vulnerabilities: add the package manager's audit workflow or an existing organization scanner when the project ships or deploys artifacts.
- Dead code and import cleanup: prefer Ruff rules first; add specialized tools only when they solve a concrete maintenance problem.

Keep the baseline strict enough to catch real defects but small enough to pass on a fresh project. Escalate strictness after the first clean run instead of starting with a noisy ruleset.

## Tool Existence and User-Home Install

Before adding a tool to a new project, check whether it already exists and whether the repo has a pinned workflow. Do not use `sudo` for project tools; install user-level CLIs only when the user agrees.

| Tool | Check existence | User-home install | Notes |
| --- | --- | --- | --- |
| `uv` | `command -v uv && uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Installs under the user's home bin path. Prefer this for Python CLI tools when available. |
| `Poetry` | `command -v poetry && poetry --version` | `curl -sSL https://install.python-poetry.org \| python3.12 -` | Use only when chosen as the project manager or repo standard. |
| `PDM` | `command -v pdm && pdm --version` | `uv tool install pdm` | If `uv` is not available, ask before using another installer. |
| `Hatch` | `command -v hatch && hatch --version` | `uv tool install hatch` | Use for Hatch environment/build workflows. |
| `pip` | `python3.12 -m pip --version` | Comes with most Python installs; upgrade user-local with `python3.12 -m pip install --user --upgrade pip`. | Keep `pip --user` for legacy/simple cases. |
| `venv` | `python3.12 -m venv --help` | Comes with Python when the OS package includes `venv`; if missing, ask before system package changes. | Do not create a virtualenv unless the repo workflow requires it. |
| `pytest` | `command -v pytest && pytest --version` | `uv tool install pytest` | Prefer project dev dependency for reproducible test runs. |
| `ruff` | `command -v ruff && ruff --version` | `uv tool install ruff` | Covers formatting, import sorting, and common linting. |
| `mypy` | `command -v mypy && mypy --version` | `uv tool install mypy` | Choose either `mypy` or `pyright` unless repo policy says both. |
| `pyright` | `command -v pyright && pyright --version` | `npm config set prefix "$HOME/.local" && npm install -g pyright` | Requires Node/npm. Prefer repo-standard type checker. |
| `bandit` | `command -v bandit && bandit --version` | `uv tool install bandit` | Add only when security static analysis is relevant. |
| `pre-commit` | `command -v pre-commit && pre-commit --version` | `uv tool install pre-commit` | Use for local hooks; CI remains the authority. |
| `hatchling` | `python3.12 -m pip show hatchling` | Prefer `[build-system].requires = ["hatchling"]`; user-home fallback is `python3.12 -m pip install --user hatchling`. | It is a build backend, not the normal command users run. |

## Setup Rules

- Prefer `src/` layout for packages because it catches packaging/import mistakes earlier than flat layout.
- Do not make top-level Python packages beside project config unless the project has a specific reason to use flat layout.
- Put executable entry points in `[project.scripts]`; do not rely on ad hoc shell wrappers for package CLIs.
- Keep runtime dependencies under `[project.dependencies]`; keep test/lint/type tools out of published metadata.
- Commit the lockfile produced by the chosen tool for applications and internal projects. For published libraries, follow the repo policy on lockfiles and keep dependency ranges honest.
- Keep generated directories such as `.venv/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `dist/`, and build artifacts out of version control.
- Add `py.typed` when typed package code is intended for downstream users.

## Git Ignore Baseline

Create `.gitignore` early. Start with common generated and local-only paths, then add project-specific entries:

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
.env.*
!.env.example
.pytest_cache/
.ruff_cache/
.mypy_cache/
.pyright/
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

Keep lockfiles tracked unless the chosen package manager's documented workflow or repo policy says otherwise.

## Pre-Commit Baseline

Propose pre-commit hooks after the toolchain is chosen. Keep them fast and deterministic:

- General hygiene: `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`, `check-json`, `check-added-large-files`.
- Python format/lint: `ruff-format` and `ruff` if the project uses Ruff.
- Type checking: prefer CI for full `mypy`/`pyright`; add a pre-commit type hook only for small projects where it stays fast.
- Security and secrets: add `bandit` or a secret scanner when the project will touch credentials, tokens, cloud config, subprocesses, or customer data.

Run hooks on all files once before the first commit, then keep CI as the authority for the same checks.

## Minimal Commands

When `uv` is available and allowed:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run bandit -q -r src
```

If the repo uses `pyright`, replace the `mypy` command with the selected package-manager equivalent of `pyright`. If `bandit` is not selected, omit it. If the repo does not use `uv`, use the local team workflow and keep equivalent commands in project scripts, CI, or documentation.

## Validation Checklist

- `pyproject.toml` parses and contains `[build-system]`, `[project]`, and tool sections that match the chosen tools.
- The import package lives under `src/` and imports only after project installation or a project-aware runner.
- Tests import the installed package path, not accidental root files.
- Lint, format-check, type-check, and test commands run from a clean checkout.
- Security/dependency scanning is either configured or explicitly deferred with a reason.
- The README states the supported Python version and the canonical setup/test commands.
- `.gitignore` covers local environments, caches, build output, coverage, and secrets files.
- The pre-commit proposal matches the selected toolchain and does not introduce slow hooks without user agreement.
- The directory tree contains no speculative folders.

## Source Anchors

- Python `pyproject.toml` metadata and tool config: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- Python `src/` layout rationale: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python dependency groups: https://packaging.python.org/en/latest/specifications/dependency-groups/
- uv project workflow: https://docs.astral.sh/uv/guides/projects/
- uv installation: https://docs.astral.sh/uv/getting-started/installation/
- Ruff linter: https://docs.astral.sh/ruff/linter/
- Ruff formatter: https://docs.astral.sh/ruff/formatter/
- mypy documentation: https://mypy.readthedocs.io/
- Pyright documentation: https://microsoft.github.io/pyright/
- Bandit documentation: https://bandit.readthedocs.io/
- Poetry documentation: https://python-poetry.org/docs/
- PDM dependency management: https://pdm-project.org/latest/usage/dependency/
- PDM installation: https://pdm-project.org/latest/#installation
- Hatch documentation: https://hatch.pypa.io/
- pre-commit documentation: https://pre-commit.com/
