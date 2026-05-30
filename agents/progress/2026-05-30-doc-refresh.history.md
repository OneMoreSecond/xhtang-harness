---

agent: Codex
time: 2026-05-30 13:54:43

Created `agents/progress/2026-05-30-doc-refresh.md` for the request to review `README.md` and `USAGE.md`. Recorded current findings: the runtime is now provider-backed, `USAGE.md` should avoid making file-writing the minimal example, `--no-stream` should be documented carefully, and path/default claims should match current config code. [source: user request, `README.md`, `USAGE.md`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/config.py`, `src/xhtang_harness/tools/builtin.py`, `src/xhtang_harness/skills.py`, `tests/test_cli.py`]

---

agent: Codex
time: 2026-05-30 13:57:41

Patched `README.md` and `USAGE.md` to match the current implementation. Removed stale demo-centered wording, replaced the minimal usage example with a simple provider-backed prompt, moved the Fibonacci file-write prompt into an explicit local-file-change section, documented the current `--no-stream` caveat, and added source labels for user-facing claims. Validation passed for `uv run pytest`, `uv run ruff check .`, and `uv run mypy src`; `uv run ruff format --check .` still fails only because existing tracked file `examples/fib30.py` would be reformatted. Local validation caches were removed. [source: user request, `README.md`, `USAGE.md`, command output]
