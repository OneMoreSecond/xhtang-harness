# Usage

This guide is for users running `xhtang-harness` from a local checkout or git worktree. [source: `README.md`]

## Source Labels

| Label | Source |
| --- | --- |
| README | `README.md` |
| Current CLI | `src/xhtang_harness/cli.py` |
| Version | `src/xhtang_harness/__init__.py` |
| MVP | `doc/mvp.md` |
| External interfaces | `doc/external-interfaces.md` |
| Storage | `doc/persistent-data-storage.md` |
| Runtime | `doc/runtime-flow-and-reliability.md` |
| UX | `doc/ux-expectations.md` |
| DeepSeek | `.agents/skills/deepseek-api/SKILL.md` |
| MVP implementation | `agents/2026-05-30-mvp-implementation.md` |

## Current Status

| Status | Meaning | Source |
| --- | --- | --- |
| Current checkout | The CLI currently runs a demo command and prints `status: ready`; it does not yet call DeepSeek, run tools, or write SQLite state. | [source: Current CLI] |
| Target MVP | The MVP design adds a DeepSeek-backed agent loop with streaming progress, optional safe tool execution, local SQLite state, cancellation, and classified errors. | [source: MVP] |
| Planned settings | Options such as `--thinking`, `--session`, `--state-path`, `--json`, and `--debug` are defined by the MVP external-interface design, but they are not implemented in the current parser yet. | [source: Current CLI, External interfaces] |

## Requirements

| Requirement | Why | Source |
| --- | --- | --- |
| `uv` | Project setup and commands are run through uv. | [source: README] |
| Python 3.12 | uv selects Python 3.12 from `.python-version`. | [source: README] |
| `DEEPSEEK_API_KEY` | Required for real DeepSeek provider calls in the target MVP. | [source: External interfaces, DeepSeek] |

Set up the local environment: [source: README]

```bash
uv sync
```

## Minimal Use

### Current Demo

Run the command that exists in the current checkout: [source: README, Current CLI]

```bash
uv run xhtang-harness "Show a usable agent harness demo"
```

Expected output shape: [source: Current CLI, Version]

```text
xhtang-harness demo
version: 0.1.0
goal: Show a usable agent harness demo
status: ready
```

You can also run the package as a module: [source: README]

```bash
uv run python -m xhtang_harness "Show a usable agent harness demo"
```

### Target MVP Real-Agent Run

When the MVP runtime is implemented, configure a DeepSeek key in the process environment and run a prompt from the checkout: [source: MVP, External interfaces, DeepSeek]

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
uv run xhtang-harness --thinking enabled "Use the current time tool and answer with the result."
```

Expected target-MVP behavior: [source: MVP, Runtime, UX]

| Step | User-visible behavior | Source |
| --- | --- | --- |
| Start | The CLI acknowledges the run before provider work begins. | [source: UX, Runtime] |
| Stream | Answer text and status events appear before the full run completes. | [source: UX, Runtime] |
| Tool call | If the model requests a safe built-in tool, the CLI shows tool status and feeds the result back to the model. | [source: MVP, Runtime] |
| Finish | The final answer is printed and the run is persisted locally. | [source: MVP, Storage] |

## Settings And Customization

### Current CLI Settings

| Setting | Example | Behavior | Source |
| --- | --- | --- | --- |
| Goal text | `uv run xhtang-harness "hello"` | Prints the normalized goal in the demo output. | [source: Current CLI] |
| Default goal | `uv run xhtang-harness` | Uses `Show a usable agent harness demo`. | [source: Current CLI] |
| Version | `uv run xhtang-harness --version` | Prints the package version and exits. | [source: Current CLI, Version] |

### Planned MVP Command Settings

| Setting | Example | Target behavior | Source |
| --- | --- | --- | --- |
| Prompt | `uv run xhtang-harness "summarize this"` | Starts a non-interactive run from the prompt argument. | [source: External interfaces, MVP] |
| Session | `--session my-session` | Continues or selects a persisted session. | [source: External interfaces, Storage] |
| Thinking mode | `--thinking enabled` or `--thinking disabled` | Selects DeepSeek thinking or non-thinking mode explicitly. | [source: External interfaces, DeepSeek] |
| Reasoning effort | `--reasoning-effort high` or `--reasoning-effort max` | Controls DeepSeek reasoning effort when thinking is enabled. | [source: External interfaces, DeepSeek] |
| Streaming | `--stream` or `--no-stream` | Enables or disables line-oriented streamed output. | [source: External interfaces, UX] |
| JSON output | `--json` | Requests machine-readable output from the provider path. | [source: External interfaces, DeepSeek] |
| State path | `--state-path .xhtang-harness/state.sqlite3` | Overrides the SQLite database location. | [source: External interfaces, Storage] |
| Debug | `--debug` | Enables additional diagnostics for local troubleshooting. | [source: External interfaces, Runtime] |

### Environment Variables

| Variable | Required | Target behavior | Source |
| --- | --- | --- | --- |
| `DEEPSEEK_API_KEY` | Yes for real provider calls | Authenticates DeepSeek requests. | [source: External interfaces, DeepSeek] |
| `DEEPSEEK_BASE_URL` | No | Overrides the DeepSeek-compatible base URL. | [source: External interfaces, DeepSeek] |
| `DEEPSEEK_MODEL` | No | Overrides the model; the design prefers `deepseek-v4-pro` for the MVP. | [source: External interfaces, DeepSeek] |
| `XHTANG_HARNESS_THINKING` | No | Sets the default thinking mode when no command option is provided. | [source: External interfaces, DeepSeek] |
| `XHTANG_HARNESS_REASONING_EFFORT` | No | Sets the default reasoning effort when no command option is provided. | [source: External interfaces, DeepSeek] |
| `XHTANG_HARNESS_STATE_PATH` | No | Overrides the SQLite state database path. | [source: External interfaces, Storage] |
| `XHTANG_HARNESS_LOG_LEVEL` | No | Sets local diagnostics verbosity. | [source: External interfaces, Runtime] |
| `XHTANG_HARNESS_USER_ID` | No | Sends a non-private user isolation ID to DeepSeek. | [source: External interfaces, DeepSeek] |

Rules for secrets and identifiers: [source: External interfaces, Storage, DeepSeek]

- Keep `DEEPSEEK_API_KEY` in the environment or an external secret manager; the harness design does not store API keys on disk. [source: External interfaces, Storage]
- Do not put private personal data in `XHTANG_HARNESS_USER_ID`; the DeepSeek guidance treats `user_id` as a non-private isolation value. [source: External interfaces, DeepSeek]

### Disk Configuration

The planned MVP may read `.xhtang-harness/config.toml` from the current worktree. Configuration precedence is command argument, then environment variable, then disk config, then code default. [source: External interfaces]

Example shape for future config: [source: External interfaces]

```toml
thinking = "enabled"
reasoning_effort = "high"
state_path = ".xhtang-harness/state.sqlite3"
log_level = "info"
```

Do not put API keys in this file. [source: External interfaces, Storage]

## Files And Worktrees

| File or directory | Current demo | Target MVP behavior | Source |
| --- | --- | --- | --- |
| `.xhtang-harness/state.sqlite3` | Not written by the current demo. | Stores sessions, runs, messages, tool calls, events, and provider usage. | [source: Current CLI, Storage] |
| `.xhtang-harness/logs/harness.log` | Not written by the current demo. | Stores diagnostics when file logging is enabled. | [source: Current CLI, External interfaces] |
| `.xhtang-harness/artifacts/<run-id>/` | Not written by the current demo. | Stores files created by tools during a run. | [source: Current CLI, External interfaces] |
| `stdout` | Prints demo text. | Prints status events and final answers. | [source: Current CLI, External interfaces, UX] |
| `stderr` | Used by argparse for command errors. | Prints command-level failures and may report run-level failures through events. | [source: Current CLI, External interfaces] |

For simultaneous worktree runs, keep the default `.xhtang-harness/` directory worktree-local. Share state across worktrees only when you intentionally pass the same `--state-path` or set the same `XHTANG_HARNESS_STATE_PATH`. [source: MVP implementation, External interfaces]

## FAQ And Troubleshooting

| Question or symptom | Meaning | What to do | Source |
| --- | --- | --- | --- |
| Why does it only print `status: ready`? | The current checkout implements only the demo CLI. | Use the current demo command for now; the DeepSeek-backed loop is target-MVP behavior. | [source: Current CLI, MVP] |
| Why does `--thinking` or `--state-path` fail with an unrecognized argument error? | Those options are planned MVP settings, not implemented in the current parser. | Use only the current CLI settings until the MVP parser is implemented. | [source: Current CLI, External interfaces] |
| `uv` is not found. | The project commands require uv. | Install uv in the development environment, then run `uv sync`. | [source: README] |
| Python version problems during setup. | The project expects Python 3.12 selected by uv. | Run `uv sync` from the repository root so uv can use `.python-version`. | [source: README] |
| Missing API key in a real-agent run. | Real DeepSeek calls require `DEEPSEEK_API_KEY`. | Set `DEEPSEEK_API_KEY` in the process environment before running the MVP command. | [source: External interfaces, DeepSeek] |
| DeepSeek returns 401. | The API key is missing or invalid. | Check the `DEEPSEEK_API_KEY` value and the environment used by `uv run`. | [source: DeepSeek] |
| DeepSeek returns 402. | The account has a billing or balance problem. | Fix the account balance or billing state before retrying. | [source: DeepSeek] |
| DeepSeek returns 429. | The account or model is rate-limited or concurrency-limited. | Retry with bounded backoff and reduce parallel runs. | [source: DeepSeek, Runtime] |
| DeepSeek returns 500 or 503. | The provider is temporarily failing or busy. | Retry with bounded backoff; keep the failed run persisted for inspection. | [source: DeepSeek, Runtime, Storage] |
| JSON output is empty or truncated. | JSON mode needs a clear JSON instruction and enough output budget. | Include the word `json`, provide a concrete schema or example, and reduce the requested payload if it is too large. | [source: DeepSeek] |
| Reasoning text is not shown. | Provider reasoning is internal by default. | Inspect debug or persisted state only when explicitly supported; normal output should show final answer and tool status, not raw reasoning. | [source: DeepSeek, UX, Storage] |
| Session history appears missing between worktrees. | Default state is worktree-local. | Use the same explicit `--state-path` or `XHTANG_HARNESS_STATE_PATH` only when shared history is intended. | [source: MVP implementation, External interfaces] |
| A shared SQLite database feels busy during parallel runs. | Simultaneous processes can contend for one database. | Prefer separate worktree-local state for parallel development, or keep shared runs short and retry later. | [source: MVP implementation, Storage] |
| Where are files written? | The target MVP keeps runtime files under `.xhtang-harness/` unless the user gives an explicit output path. | Check `.xhtang-harness/state.sqlite3`, `.xhtang-harness/logs/`, and `.xhtang-harness/artifacts/` after MVP runtime features are implemented. | [source: External interfaces, Storage] |
| How do I verify this checkout? | The project defines local checks through uv. | Run `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src`. | [source: README] |

## Development Checks

Run these commands from the repository root when validating local changes: [source: README]

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
