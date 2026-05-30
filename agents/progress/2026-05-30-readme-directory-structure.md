Task ID: 2026-05-30-readme-directory-structure

# README Directory Structure

## Background

The user requested a summary of the current directory structure in `README.md`. [source: user instruction]

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Directory structure | The main source, documentation, test, example, and support paths in the repository. | `find . -maxdepth 3` |
| Generated directory | Local environment, cache, or runtime state directory not treated as source layout. | `.gitignore`, `git status --short --ignored` |

- `README.md` currently contains project overview, requirements, setup, MVP run commands, built-in tools, and checks. [source: `README.md`]
- The repository currently has source code in `src/xhtang_harness/`, tests in `tests/`, design docs in `doc/`, task records in `agents/`, local skills in `.agents/skills/`, and examples in `examples/`. [source: `find . -maxdepth 3 -type d`, `find . -maxdepth 3 -type f`]
- `bin/` and `agents/tmp/` currently have no files to summarize as source content. [source: `find bin -maxdepth 2 -type f`, `find agents/tmp -maxdepth 3 -type f`]

## Constraint and Assumption

- Update only `README.md` and task tracking files for this documentation request. [source: user instruction]
- Keep the directory summary concise and focused on paths a reader would care about. [source: user instruction]
- Do not modify unrelated code or existing user changes. [source: `git status --short`]

## Challenges

- The repository contains generated or empty directories that would make the summary noisy if listed directly. [source: `find . -maxdepth 3 -type d`, `.gitignore`]

## Decisions

- Add a `Directory Structure` table to `README.md` after the built-in tools section and before checks. [source: `README.md`]
- Include a source column in the table to satisfy document clarity requirements. [source: `AGENTS.md`]
- Omit empty/generated directories from the main table and mention generated local directories separately. [source: `.gitignore`, `find` output]

## Design

- The README section lists top-level project areas and important root files with one-line purposes. [source: design decision]
- Generated local directories are called out as not part of the source layout. [source: `.gitignore`]

## Todo

- [x] Inspect README and current directory layout.
- [x] Add README directory structure summary.
- [x] Create progress and history files.
- [x] Review markdown and current diff.

## Results

- Added a `Directory Structure` section to `README.md`. [source: code changes]
- The summary covers `.agents/skills/`, `agents/`, `doc/`, `examples/`, `src/xhtang_harness/`, `tests/`, key root docs/config files, and generated-directory handling. [source: `README.md`]
- Reviewed the rendered markdown content and diff. [source: `sed -n '1,220p' README.md`, `git diff -- README.md agents/progress/2026-05-30-readme-directory-structure.md agents/progress/2026-05-30-readme-directory-structure.history.md`]
