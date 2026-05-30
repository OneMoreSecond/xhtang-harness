Task ID: 2026-05-30-doc-audience-split

# Documentation Audience Split

## Background

The user requested changing the current `README.md` into `CONTRIBUTION.md` with developers as the audience, and moving or integrating application-user content into `USAGE.md`. [source: user instruction]

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Developer documentation | Setup, structure, implementation map, local state, tools, and checks for engineers working on the repository. | `README.md`, `src/xhtang_harness/` |
| Application-user documentation | Setup, prompts, options, environment variables, local files, and troubleshooting for people running the CLI. | `USAGE.md`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/config.py` |

- `README.md` mixed developer details, source labels, setup, run commands, built-in tools, directory structure, and checks. [source: `README.md` before edit]
- `USAGE.md` already contained most application-user material but also included source labels and check commands. [source: `USAGE.md` before edit]
- `pyproject.toml` used `README.md` as the project readme, so deleting `README.md` requires updating the metadata readme path. [source: `pyproject.toml`]
- Design docs still referenced `README.md` as a source label after the split. [source: `doc/external-interfaces.md`, `doc/module-responsibilities.md`, `doc/ux-expectations.md`]

## Constraint and Assumption

- Treat `CONTRIBUTION.md` as the developer-facing replacement for the old README. [source: user instruction]
- Keep `USAGE.md` focused on application users and avoid source labels in that file. [source: user instruction]
- Update `pyproject.toml` to point at `USAGE.md` because package metadata should not reference a deleted file. [source: `pyproject.toml`, design decision]
- Avoid modifying unrelated runtime changes currently present in the worktree. [source: `git status --short`]

## Challenges

- Existing docs contained overlapping setup and run content, so the split needed to preserve useful user instructions without duplicating developer implementation detail. [source: `README.md`, `USAGE.md`]

## Decisions

- Delete `README.md` and create `CONTRIBUTION.md` from its developer-oriented content. [source: user instruction]
- Rewrite `USAGE.md` as the application-user guide, keeping setup, run examples, local file-change guidance, skills, options, environment variables, local files, and troubleshooting. [source: user instruction]
- Change `pyproject.toml` `readme` from `README.md` to `USAGE.md`. [source: `pyproject.toml`]
- Replace active design-doc references to `README.md` with `USAGE.md` or `CONTRIBUTION.md` labels where appropriate. [source: `doc/external-interfaces.md`, `doc/module-responsibilities.md`, `doc/ux-expectations.md`]

## Design

- `CONTRIBUTION.md` covers requirements, setup, developer run commands, directory structure, implementation map, local state/skills, built-in tools, checks, and lockfile maintenance. [source: design decision]
- `USAGE.md` covers requirements, setup, minimal run, explicit local file changes, skills, options, environment variables, local files, and troubleshooting. [source: design decision]
- `USAGE.md` avoids source labels and minimizes internal terms such as provider and SQLite. [source: user instruction, design decision]

## Todo

- [x] Inspect current README, USAGE, pyproject, and CLI/config surfaces.
- [x] Create developer-focused `CONTRIBUTION.md`.
- [x] Move/integrate application-user content into `USAGE.md`.
- [x] Remove `README.md` and update package readme metadata.
- [x] Update active design-doc references to the removed `README.md`.
- [x] Validate docs/config and review diff.

## Results

- Created `CONTRIBUTION.md` for developer-facing content. [source: code changes]
- Rewrote `USAGE.md` for application users without source labels. [source: code changes]
- Simplified internal-ish terms in `USAGE.md`, replacing provider/SQLite wording with DeepSeek/local-state wording where possible. [source: code changes]
- Removed `README.md` and updated `pyproject.toml` to use `USAGE.md` as package metadata readme. [source: code changes]
- Updated active design docs that referenced `README.md`. [source: `doc/external-interfaces.md`, `doc/module-responsibilities.md`, `doc/ux-expectations.md`]
- Validation passed: `uv lock --check`, `uv run xhtang-harness --version`, `uv build`, and targeted scans for stale README references and implementation/source terms in `USAGE.md`. Generated build/runtime artifacts were removed after validation. [source: command output]
