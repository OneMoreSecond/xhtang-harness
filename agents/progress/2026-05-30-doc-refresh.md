Task ID: 2026-05-30-doc-refresh

# README And Usage Refresh

## Original Request

please review README.md and USAGE.md to remove or correct outdated information

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| README | Project overview and quick-start documentation. | [source: user request, `README.md`] |
| Usage guide | End-user CLI guide for running the harness. | [source: user request, `USAGE.md`] |
| Current CLI | The implemented `xhtang-harness` parser and renderer. | [source: `src/xhtang_harness/cli.py`, `uv run xhtang-harness --help`] |
| Current runtime | The implemented app, agent loop, storage, tools, skills, and DeepSeek provider behavior. | [source: `src/xhtang_harness/app.py`, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/storage/sqlite.py`, `src/xhtang_harness/tools/builtin.py`, `src/xhtang_harness/skills.py`, `src/xhtang_harness/providers/deepseek.py`] |

- `README.md` already describes the harness as DeepSeek-backed and lists implemented options, built-in tools, local skills, and skill learning. [source: `README.md`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/tools/builtin.py`, `src/xhtang_harness/skills.py`]
- `USAGE.md` overemphasizes a file-writing Fibonacci task as the MVP goal; a safer minimal run should use the `get_current_time` tool, with bash file writes documented as an explicit-change example. [source: `USAGE.md`, `src/xhtang_harness/tools/builtin.py`, design decision]
- `--no-stream` is parsed into config, but current CLI rendering still prints `answer_delta` events; docs should not claim output filtering behavior that is not implemented. [source: `src/xhtang_harness/cli.py`, `tests/test_cli.py`]
- The default state path is worktree-local `.xhtang-harness/state.sqlite3`, and default skills path is worktree-local `.skills`. [source: `src/xhtang_harness/config.py`, `tests/test_config.py`]
- Local skill matching is exact substring matching against the skill `name` or `description` in the prompt. [source: `src/xhtang_harness/skills.py`, `tests/test_agent_loop.py`]
- `DEEPSEEK_API_KEY` is required before real provider calls start. [source: `src/xhtang_harness/app.py`, `src/xhtang_harness/config.py`]

## Constraint and Assumption

- This task is documentation-only. [source: user request]
- Do not modify runtime code or unrelated existing files while correcting README and USAGE. [source: user request, `AGENTS.md`]
- Keep command examples runnable from the current checkout with `uv run`. [source: `README.md`, `src/xhtang_harness/cli.py`]
- Keep DeepSeek-specific facts aligned with local provider guidance. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Facts added to markdown should include information sources. [source: `AGENTS.md`]

## Challenges

- The docs need to be concise but still distinguish implemented behavior from user-controlled provider/model behavior. [source: `README.md`, `USAGE.md`, design decision]
- The `--no-stream` option exists but its current user-visible behavior is narrower than its help text implies. [source: `src/xhtang_harness/cli.py`, `tests/test_cli.py`]
- The bash tool can change files, so examples should make local mutation explicit and not present file writes as the safest minimal run. [source: `src/xhtang_harness/tools/builtin.py`, design decision]

## Decisions

- Refresh README quick-start examples around simple provider/tool runs instead of "demo" wording. [source: `README.md`, `src/xhtang_harness/cli.py`]
- Refresh USAGE around a minimal `get_current_time` run, with a separate explicit bash file-write example. [source: `USAGE.md`, `src/xhtang_harness/tools/builtin.py`]
- Add source labels and source columns where useful so documentation claims remain traceable. [source: `AGENTS.md`, design decision]
- Document the current `--no-stream` caveat instead of implying full stream filtering. [source: `src/xhtang_harness/cli.py`, `tests/test_cli.py`]

## Design

Update only `README.md`, `USAGE.md`, and this task log. [source: user request, design decision]

The refreshed docs should include: [source: design decision]

- Requirements and setup. [source: `README.md`, `pyproject.toml`]
- Minimal provider-backed command examples. [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/app.py`]
- Built-in tools and skill-learning behavior. [source: `src/xhtang_harness/tools/builtin.py`, `src/xhtang_harness/skills.py`]
- State and skill path defaults. [source: `src/xhtang_harness/config.py`]
- Troubleshooting for API key, uv/Python setup, local skills, JSON mode, and `--no-stream`. [source: `USAGE.md`, `.agents/skills/deepseek-api/SKILL.md`, `tests/test_cli.py`]

## Todo

- [x] Read README and USAGE. [source: task work]
- [x] Compare docs with current CLI/runtime code and tests. [source: task work]
- [x] Create task progress and history files. [source: task work]
- [x] Patch README and USAGE. [source: user request]
- [x] Run checks and update results. [source: `AGENTS.md`]

## Results

Updated `README.md` and `USAGE.md` to remove stale demo framing, use a safer minimal provider-backed prompt, move Fibonacci file creation into an explicit local-file-change example, document current `--no-stream` behavior, add source labels, and align state, skill, tool, and environment-variable details with current code. [source: `README.md`, `USAGE.md`, task work]

Validation results: `uv run pytest` passed with 50 tests, `uv run ruff check .` passed, and `uv run mypy src` passed. `uv run ruff format --check .` still fails because existing tracked file `examples/fib30.py` would be reformatted; this documentation task did not touch that file. Local validation caches were removed after the run. [source: command output]
