Task ID: 2026-05-30-require-initial-goal

# Require Initial Goal

## Original Request

require initial goal input. raise on blank

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Initial goal | The first positional prompt passed to `xhtang-harness`. | [source: user request, `src/xhtang_harness/cli.py`] |
| Blank prompt | A prompt that is empty after whitespace trimming. | [source: `src/xhtang_harness/config.py`] |
| Initial prompt request | CLI prompt shown before a run starts when the positional `goal` was omitted. | [source: user update, design decision] |

- Latest user update says that if goal is not given, the CLI should ask the user before beginning. [source: user update]
- The CLI previously changed `goal` to a required positional argument; this must be revised to an optional positional with no default goal. [source: `src/xhtang_harness/cli.py`, task history]
- `load_config` already strips prompt text and raises `ConfigError("prompt must not be empty")` for blank prompts. [source: `src/xhtang_harness/config.py`]
- Existing follow-up prompt logic reads an additional prompt from interactive stdin after completed runs; the initial prompt should use a separate message before the first run. [source: `src/xhtang_harness/cli.py`]
- `USAGE.md` must say omitted initial goals are prompted, not rejected by argparse. [source: `USAGE.md`, user update]

## Constraint and Assumption

- This is a behavior change for the initial CLI invocation only. [source: user request, user update]
- Additional interactive prompts may still use blank input to exit the interactive follow-up loop. [source: `src/xhtang_harness/cli.py`, design decision]
- Do not change unrelated existing worktree modifications, including deleted `README.md` and other documentation changes. [source: `git status --short`, `AGENTS.md`]
- Keep blank initial prompts rejected through the existing `ConfigError` path, whether the blank came from an argument or the interactive initial prompt. [source: `src/xhtang_harness/config.py`, design decision]

## Challenges

- Missing goal should prompt before run setup, while blank input should still fail before provider or storage work starts. [source: user update, `src/xhtang_harness/config.py`]
- Non-interactive stdin may return EOF; in that case the empty input should take the same blank-prompt validation path. [source: design decision]

## Decisions

- Keep `goal` optional at the parser level, but do not provide a default prompt. [source: user update, design decision]
- If `goal` is omitted, print `initial goal: ` to stderr and read one line from stdin before constructing config. [source: user update, design decision]
- Keep demo-only `DEFAULT_GOAL` and `render_demo` removed. [source: design decision]
- Add CLI tests for prompted missing goal, blank argument, and blank prompted input. [source: user request, user update, `tests/test_cli.py`]
- Update the current `USAGE.md` option row to say omitted `goal` prompts before beginning and blank prompts are rejected. [source: `USAGE.md`, design decision]

## Design

`build_parser` will define `goal` as an optional positional argument with no default prompt. `main([])` will print `initial goal: ` to stderr, read one line from stdin, and pass that value to `load_config`. `main([" "])` and `main([])` followed by blank input will return exit code `2` and print `config_error: prompt must not be empty` through existing config validation. [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/config.py`, design decision]

## Todo

- [x] Inspect current CLI parser, config validation, tests, and usage docs. [source: task work]
- [x] Create task progress and history files. [source: task work]
- [x] Make missing initial `goal` prompt before beginning. [source: user update]
- [x] Remove stale demo default helper tests. [source: design decision]
- [x] Add missing-goal prompt and blank-goal test coverage. [source: user request, user update]
- [x] Run checks and update results. [source: `AGENTS.md`]

## Results

Updated `xhtang_harness.cli` so omitted initial `goal` input prompts with `initial goal: ` before run setup and still uses no demo default. Removed demo-only `DEFAULT_GOAL` and `render_demo`. Blank initial prompts still fail through `ConfigError("prompt must not be empty")`. [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/config.py`]

Updated CLI tests to cover prompted missing initial goal, blank argument goal, and blank prompted goal. Updated `USAGE.md` to explain that omitted `goal` input prompts before beginning and blank prompts are rejected. [source: `tests/test_cli.py`, `USAGE.md`]

Validation results after the user update: `uv run pytest tests/test_cli.py` passed with 9 tests, full `uv run pytest` passed with 54 tests, `uv run ruff format --check .` passed, and `uv run mypy src` passed. Manual CLI checks confirmed `printf '   \n' | uv run xhtang-harness` prints `initial goal: config_error: prompt must not be empty`, and `printf 'hello\n' | uv run xhtang-harness` prompts for the goal before beginning and completed a live provider-backed run in this environment. `uv run ruff check .` failed only on existing tracked file `examples/fib30.py` for `B905 zip() without strict=`, which this task did not touch. Local validation caches and generated `.xhtang-harness/state.sqlite3` from the manual run were removed after the run. [source: command output]
