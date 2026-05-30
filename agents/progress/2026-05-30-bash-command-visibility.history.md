---

agent: Codex
time: 2026-05-30 14:00:20

Created `agents/progress/2026-05-30-bash-command-visibility.md` for the request to print the bash command for bash tool calls even without debug mode. Recorded the current event/rendering path and planned to add `command` to `tool_call_started` only for bash calls with a string `command` argument. [source: user request, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`, `src/xhtang_harness/tools/builtin.py`]

---

agent: Codex
time: 2026-05-30 14:02:23

Implemented bash command visibility by adding `command` to `tool_call_started` events for bash calls and rendering it in normal CLI output without requiring `--debug`. Added tests in `tests/test_agent_loop.py` and `tests/test_cli.py`; updated `README.md` and `USAGE.md` to document the behavior. Focused tests and full pytest passed; `ruff format --check` and mypy passed; `ruff check` failed only on pre-existing `examples/fib30.py` B905. Local validation caches were removed. [source: user request, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`, `tests/test_agent_loop.py`, `tests/test_cli.py`, `README.md`, `USAGE.md`, command output]
