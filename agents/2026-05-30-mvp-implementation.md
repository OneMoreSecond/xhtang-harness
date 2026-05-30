Task ID: 2026-05-30-mvp-implementation

# MVP Implementation Plan

## Original Request

now create a detailed implementation plan agents/2026-05-30-mvp-implementation.md for MVP, based on current design.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| MVP | Smallest implementation that can run a useful local agent loop end to end. | [source: `doc/mvp.md`] |
| Agent loop | Runtime flow that calls the provider, handles tool calls, appends tool results, and returns final output. | [source: `doc/runtime-flow-and-reliability.md`] |
| Event stream | Ordered runtime updates consumed by the CLI and optionally persisted. | [source: `doc/runtime-flow-and-reliability.md`, `doc/ux-expectations.md`] |
| Provider adapter | Module boundary that translates normalized harness requests to DeepSeek API calls and translates provider responses to harness events. | [source: `doc/module-responsibilities.md`] |
| Storage gateway | Module that owns durable SQLite reads and writes. | [source: `doc/module-responsibilities.md`, `doc/persistent-data-storage.md`] |
| External interface | Command argument, environment variable, disk input, output file, stdout, stderr, or exit code boundary. | [source: `doc/external-interfaces.md`] |
| Worktree run | One harness invocation from a specific git checkout/worktree with its own current working directory. | [source: user follow-up, `README.md`, design decision] |
| Parallel separation | Isolation of state, logs, artifacts, and temporary runtime files so simultaneous runs from multiple worktrees do not collide. | [source: user follow-up, design decision] |
| Skeleton file | Placeholder source or test file that reserves a module boundary for parallel development but does not implement behavior yet. | [source: user instruction, design decision] |

- Current package source lives under `src/xhtang_harness/`, tests live under `tests/`, package metadata is in `pyproject.toml`, and the CLI entry point is `xhtang_harness.cli:main`. [source: `pyproject.toml`, `README.md`]
- The canonical local workflow is `uv sync`, `uv run xhtang-harness ...`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src`. [source: `AGENTS.md`, `README.md`]
- Current runtime dependencies are empty, while the planned DeepSeek provider integration needs an HTTP/API client; the existing DeepSeek skill examples use the OpenAI-compatible SDK. [source: `pyproject.toml`, `.agents/skills/deepseek-api/SKILL.md`]
- The MVP must accept a prompt, call `deepseek-v4-pro`, stream progress, support explicit reasoning mode, persist sessions/runs/messages/tool calls/usage to SQLite, run at least one safe built-in tool, preserve thinking-mode tool-call state, support cancellation state, and classify errors. [source: `doc/mvp.md`]
- External interfaces already define command arguments, environment variables, disk inputs, output files, stdout/stderr behavior, and configuration precedence. [source: `doc/external-interfaces.md`]
- The first persistent store should be SQLite with default path `.xhtang-harness/state.sqlite3` and override `XHTANG_HARNESS_STATE_PATH`. [source: `doc/persistent-data-storage.md`]
- DeepSeek `/chat/completions` is stateless, so each provider request must include the complete conversation history. [source: `.agents/skills/deepseek-api/SKILL.md`]
- DeepSeek thinking-mode tool calls require preserving assistant `reasoning_content` and `tool_calls` in later requests. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Simultaneous runs from multiple git worktrees need explicit separation for local state, logs, tool artifacts, and config overrides. [source: user follow-up]
- User requested a directory and file skeleton based on the implementation plan; implementation and test files may be empty and do not need to be runnable yet. [source: user instruction]

## Constraint and Assumption

- Current task implements the MVP runtime based on this existing plan, then commits and pushes the finished branch. [source: user instruction on 2026-05-30]
- Previous skeleton-only constraints are superseded for the current task; runtime behavior should now be implemented. [source: user instruction on 2026-05-30, `agents/2026-05-30-mvp-implementation.history.md`]
- Keep the implementation simple and local-first; avoid a hosted service, multi-provider UI, rich TUI, or background queue for the MVP. [source: `doc/mvp.md`, `AGENTS.md`]
- Use uv as the project runner and dependency manager. [source: `AGENTS.md`, `README.md`]
- Use SQLite through Python standard library `sqlite3` for the first durable store. [source: `doc/persistent-data-storage.md`]
- Add the `openai` runtime dependency during provider implementation unless a later spike proves a smaller direct HTTP client is clearly better. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]
- Unit tests must not require a real DeepSeek API key or network access; use fake provider and fake tool implementations for deterministic tests. [source: `AGENTS.md`, design decision]
- Live DeepSeek validation is optional and should be run only when `DEEPSEEK_API_KEY` is configured by the user. [source: `doc/external-interfaces.md`, `.agents/skills/deepseek-api/SKILL.md`]
- Configuration precedence is command argument, environment variable, disk config, then code default. [source: `doc/external-interfaces.md`]
- Default runtime state should be scoped to the current worktree by placing `.xhtang-harness/` under the current working tree; shared state is allowed only when the user explicitly sets `--state-path` or `XHTANG_HARNESS_STATE_PATH`. [source: `doc/external-interfaces.md`, `doc/persistent-data-storage.md`, user follow-up]

## Challenges

- The MVP requires a real provider path, but tests must stay deterministic and offline. [source: `doc/mvp.md`, `AGENTS.md`]
- Streaming should keep the user informed without forcing a complex terminal UI. [source: `doc/ux-expectations.md`, `doc/mvp.md`]
- DeepSeek reasoning tool calls need exact message replay behavior that is easy to break if provider SDK objects leak through the app. [source: `.agents/skills/deepseek-api/SKILL.md`]
- SQLite persistence needs enough schema to resume and inspect runs without overbuilding migrations or export features. [source: `doc/persistent-data-storage.md`, `doc/mvp.md`]
- Cancellation is cooperative; the plan must record durable cancellation state without promising every active network/tool operation can stop immediately. [source: `doc/runtime-flow-and-reliability.md`]
- CLI integration should expose useful MVP arguments while keeping implementation paths testable without shelling out for every case. [source: `doc/external-interfaces.md`, `AGENTS.md`]
- Parallel worktree runs can accidentally share a user-provided SQLite path or artifact directory; the implementation must make the default isolated and warn or lock when a shared path is selected. [source: user follow-up, design decision]

## Decisions

- Implement the MVP in vertical slices ordered by dependency depth: domain/config, storage, tools, provider adapter, agent loop, CLI, then live/manual validation. [source: design decision based on `doc/module-responsibilities.md`]
- Define internal dataclasses for messages, events, tool calls, provider options, and usage before provider or storage code. [source: `doc/module-responsibilities.md`, design decision]
- Keep the provider adapter behind a narrow protocol so the agent loop can be tested with scripted fake provider responses. [source: `doc/module-responsibilities.md`, `AGENTS.md`]
- Start with one built-in safe tool named `get_current_time`, implemented with an injectable clock for tests and no filesystem side effects. [source: `doc/mvp.md`, design decision]
- Persist final messages, run status, tool calls, and usage in SQLite for the MVP; persist every stream token as an event only if event replay is enabled later. [source: `doc/persistent-data-storage.md`, `doc/mvp.md`, design decision]
- Render CLI output as line-oriented events plus final answer text, not a rich terminal UI. [source: `doc/ux-expectations.md`, `doc/mvp.md`]
- Use exit code `0` for success, `2` for usage/configuration errors, `1` for runtime/provider/tool failures, and `130` for cancellation. [source: `doc/external-interfaces.md`, design decision]
- Treat `doc/mvp.md` acceptance checks as the implementation completion gate. [source: `doc/mvp.md`]
- Add a parallel-worktree separation rule: default `.xhtang-harness/` state, logs, artifacts, and temp files are worktree-local; cross-worktree sharing must be an explicit external-interface choice. [source: user follow-up, design decision]
- Use SQLite connection timeouts and short transactions for run status/message writes so simultaneous runs in the same selected state database fail predictably or wait briefly instead of corrupting state. [source: Python `sqlite3` behavior, design decision]
- Create placeholder implementation and test files for each planned module slice so separate worktrees can implement different phases with fewer first-touch file conflicts. [source: user instruction, design decision]

## Design

### Target Module Shape

| Module | Planned files | Purpose | Source |
| --- | --- | --- | --- |
| CLI | `src/xhtang_harness/cli.py` | Parse external inputs, load config, call app service, render events, return exit code. | [source: `doc/module-responsibilities.md`, `doc/external-interfaces.md`] |
| App service | `src/xhtang_harness/app.py` | Coordinate CLI request, storage, provider, tools, and agent loop. | [source: `doc/module-responsibilities.md`] |
| Domain models | `src/xhtang_harness/conversation.py`, `src/xhtang_harness/events.py`, `src/xhtang_harness/errors.py` | Define typed internal interfaces independent of SDK and SQLite details. | [source: `doc/module-responsibilities.md`, design decision] |
| Config | `src/xhtang_harness/config.py` | Load arguments, environment variables, optional TOML config, defaults, and validation. | [source: `doc/external-interfaces.md`] |
| Storage | `src/xhtang_harness/storage/sqlite.py` | Create schema and persist sessions, runs, messages, tool calls, usage, and final states. | [source: `doc/persistent-data-storage.md`] |
| Tools | `src/xhtang_harness/tools/registry.py`, `src/xhtang_harness/tools/executor.py`, `src/xhtang_harness/tools/builtin.py` | Register safe tools, validate JSON arguments, execute tools, return tool results. | [source: `doc/module-responsibilities.md`, `doc/mvp.md`] |
| Provider | `src/xhtang_harness/providers/base.py`, `src/xhtang_harness/providers/deepseek.py` | Provide a testable provider protocol and DeepSeek implementation. | [source: `doc/module-responsibilities.md`, `.agents/skills/deepseek-api/SKILL.md`] |
| Agent loop | `src/xhtang_harness/agent_loop.py` | Execute provider/tool turns and emit/persist events until completion, failure, or cancellation. | [source: `doc/runtime-flow-and-reliability.md`] |
| Telemetry | `src/xhtang_harness/telemetry.py` | Provide structured logs and optional log-file setup. | [source: `doc/external-interfaces.md`, `doc/runtime-flow-and-reliability.md`] |

### Skeleton Files

| Slice | Source skeleton | Test skeleton | Source |
| --- | --- | --- | --- |
| App service | `src/xhtang_harness/app.py` | `tests/test_app.py` | [source: user instruction, design decision] |
| Agent loop | `src/xhtang_harness/agent_loop.py` | `tests/test_agent_loop.py` | [source: user instruction, design decision] |
| Config | `src/xhtang_harness/config.py` | `tests/test_config.py` | [source: user instruction, design decision] |
| Conversation | `src/xhtang_harness/conversation.py` | `tests/test_conversation.py` | [source: user instruction, design decision] |
| Events | `src/xhtang_harness/events.py` | `tests/test_events.py` | [source: user instruction, design decision] |
| Errors | `src/xhtang_harness/errors.py` | Future tests in relevant slices | [source: user instruction, design decision] |
| Telemetry | `src/xhtang_harness/telemetry.py` | Future tests in CLI/runtime slices | [source: user instruction, design decision] |
| Provider base | `src/xhtang_harness/providers/base.py` | `tests/providers/test_provider_base.py` | [source: user instruction, design decision] |
| DeepSeek provider | `src/xhtang_harness/providers/deepseek.py` | `tests/providers/test_deepseek.py` | [source: user instruction, design decision] |
| SQLite storage | `src/xhtang_harness/storage/sqlite.py` | `tests/storage/test_sqlite.py` | [source: user instruction, design decision] |
| Built-in tools | `src/xhtang_harness/tools/builtin.py` | `tests/tools/test_builtin.py` | [source: user instruction, design decision] |
| Tool executor | `src/xhtang_harness/tools/executor.py` | `tests/tools/test_executor.py` | [source: user instruction, design decision] |
| Tool registry | `src/xhtang_harness/tools/registry.py` | `tests/tools/test_registry.py` | [source: user instruction, design decision] |
| Parallel worktree behavior | Config/storage/runtime files above | `tests/test_parallel_worktree.py` | [source: user instruction, user follow-up] |

### Event Types

| Event | Payload minimum | Emitted by | Source |
| --- | --- | --- | --- |
| `run_started` | `run_id`, `session_id` | App or agent loop | [source: `doc/runtime-flow-and-reliability.md`] |
| `message_recorded` | `message_id`, `role` | Storage/app | [source: `doc/runtime-flow-and-reliability.md`] |
| `provider_request_started` | `model`, `thinking_mode`, `attempt` | Provider adapter | [source: `doc/runtime-flow-and-reliability.md`, `.agents/skills/deepseek-api/SKILL.md`] |
| `answer_delta` | `text` | Provider adapter | [source: `doc/ux-expectations.md`] |
| `tool_call_started` | `tool_call_id`, `name` | Tool executor | [source: `doc/runtime-flow-and-reliability.md`] |
| `tool_call_finished` | `tool_call_id`, `status`, `summary` | Tool executor | [source: `doc/runtime-flow-and-reliability.md`] |
| `retry_scheduled` | `error_class`, `delay_seconds`, `attempt` | Provider adapter or agent loop | [source: `doc/runtime-flow-and-reliability.md`] |
| `run_completed` | `run_id`, `usage_summary` | Agent loop | [source: `doc/runtime-flow-and-reliability.md`] |
| `run_failed` | `run_id`, `error_class`, `message` | Agent loop | [source: `doc/runtime-flow-and-reliability.md`] |
| `run_cancelled` | `run_id` | Agent loop | [source: `doc/runtime-flow-and-reliability.md`] |

### Storage Schema Implementation

| Table | MVP fields | Test focus | Source |
| --- | --- | --- | --- |
| `sessions` | `id`, `title`, `created_at`, `updated_at`, `status` | Create/open/update session. | [source: `doc/persistent-data-storage.md`] |
| `runs` | `id`, `session_id`, `status`, `started_at`, `ended_at`, `error_code`, `error_message` | Status transitions and cancellation/failure persistence. | [source: `doc/persistent-data-storage.md`] |
| `messages` | `id`, `session_id`, `run_id`, `role`, `content`, `reasoning_content`, `tool_call_id`, `created_at` | Full history replay and reasoning preservation. | [source: `doc/persistent-data-storage.md`, `.agents/skills/deepseek-api/SKILL.md`] |
| `tool_calls` | `id`, `run_id`, `provider_tool_call_id`, `name`, `arguments_json`, `result_text`, `status`, `error_message` | Unknown tool, invalid JSON, success, failure. | [source: `doc/persistent-data-storage.md`, `doc/mvp.md`] |
| `provider_usage` | `run_id`, `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens` | Usage insert and cache telemetry mapping. | [source: `doc/persistent-data-storage.md`, `.agents/skills/deepseek-api/SKILL.md`] |
| `events` | `id`, `run_id`, `type`, `payload_json`, `created_at` | Store coarse lifecycle events, not every token by default. | [source: `doc/persistent-data-storage.md`, design decision] |

### Parallel Worktree Separation

| Concern | Recommendation | Implementation detail | Source |
| --- | --- | --- | --- |
| Default state location | Keep each worktree isolated by default. | Resolve default state under `Path.cwd() / ".xhtang-harness" / "state.sqlite3"` at process start. | [source: user follow-up, `doc/persistent-data-storage.md`] |
| Shared state | Make sharing opt-in. | Only share across worktrees when `--state-path` or `XHTANG_HARNESS_STATE_PATH` points to the same database. | [source: user follow-up, `doc/external-interfaces.md`] |
| Run identity | Make run IDs globally unique. | Use UUIDv7/UUID4 or another collision-resistant ID for `sessions`, `runs`, tool calls, and artifact directories. | [source: user follow-up, design decision] |
| Artifacts | Separate artifacts by run. | Write tool artifacts under `.xhtang-harness/artifacts/<run-id>/` or the state-path sibling when state path is overridden. | [source: user follow-up, `doc/external-interfaces.md`] |
| Logs | Avoid one shared append target by default. | Put logs under the current worktree `.xhtang-harness/logs/`; include run ID in structured log records. | [source: user follow-up, `doc/external-interfaces.md`] |
| SQLite concurrency | Keep writes short and predictable. | Use one connection per process, `busy_timeout`, explicit transactions, and no long-running network/tool work inside a transaction. | [source: user follow-up, design decision] |
| Temp files | Avoid `/tmp` and cross-run collisions. | Put generated temp files under `.xhtang-harness/tmp/<run-id>/` unless the user provides an explicit output path. | [source: `AGENTS.md`, user follow-up, design decision] |
| Config | Keep config local unless explicitly shared. | Read `.xhtang-harness/config.toml` from the current worktree; environment variables remain process-scoped. | [source: `doc/external-interfaces.md`, user follow-up] |

### Implementation Phases

| Phase | Goal | Main outputs | Validation | Source |
| --- | --- | --- | --- | --- |
| 0 | Baseline and dependency prep | Add `openai` dependency, keep uv lock current, preserve existing CLI behavior. | `uv sync`, existing tests pass. | [source: `.agents/skills/deepseek-api/SKILL.md`, `README.md`] |
| 1 | Domain and config | Typed dataclasses, error classes, config loader, argument/env precedence. | Unit tests for config precedence and validation. | [source: `doc/external-interfaces.md`] |
| 2 | SQLite storage | Schema creation and storage gateway. | Temp-directory SQLite tests for sessions, runs, messages, usage, tool calls. | [source: `doc/persistent-data-storage.md`] |
| 3 | Tool system | Registry, executor, `get_current_time` tool. | Unit tests for schema, valid execution, unknown tool, invalid JSON, tool failure. | [source: `doc/mvp.md`, `doc/module-responsibilities.md`] |
| 4 | Provider adapter | DeepSeek provider protocol and implementation with streaming, reasoning modes, usage, errors. | Fake-client unit tests; no live key required. | [source: `.agents/skills/deepseek-api/SKILL.md`] |
| 5 | Agent loop | Provider/tool loop, full history replay, reasoning preservation, cancellation state. | Scripted fake-provider tests for simple answer, tool call, retry, failure, cancellation. | [source: `doc/runtime-flow-and-reliability.md`] |
| 6 | CLI integration | MVP command args, line-oriented event rendering, exit codes. | CLI parser tests and subprocess smoke tests using fake app or missing-key path. | [source: `doc/external-interfaces.md`, `doc/ux-expectations.md`] |
| 7 | Acceptance and docs | README usage update, manual live validation instructions, acceptance checklist. | `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`; optional live run with key. | [source: `doc/mvp.md`, `AGENTS.md`] |

## Todo

The checkboxes below track MVP implementation status for the current branch. [source: user instruction on 2026-05-30]

### Phase 0: Baseline And Dependencies

- [x] Add `openai` as a runtime dependency with uv and update `uv.lock`. [source: `.agents/skills/deepseek-api/SKILL.md`, `pyproject.toml`]
- [ ] Keep existing CLI demo behavior passing before changing runtime behavior. [source: `README.md`, `tests/test_cli.py`]
- [x] Add `.xhtang-harness/` to `.gitignore` if it is not already ignored. [source: `doc/persistent-data-storage.md`, `doc/external-interfaces.md`, `.gitignore`]

### Phase 1: Domain Models And Config

- [x] Add domain models for `Session`, `Run`, `Message`, `ToolCall`, `ProviderUsage`, and `HarnessEvent`. [source: `src/xhtang_harness/conversation.py`, `src/xhtang_harness/events.py`]
- [x] Use collision-resistant IDs for sessions, runs, messages, and tool calls; artifact directories are deferred until a file-writing tool exists. [source: `src/xhtang_harness/conversation.py`, `src/xhtang_harness/storage/sqlite.py`]
- [x] Add error classes for config, provider, tool, storage, cancellation, and user-facing run failures. [source: `src/xhtang_harness/errors.py`]
- [x] Add config loader for command arguments, environment variables, optional `.xhtang-harness/config.toml`, and defaults. [source: `src/xhtang_harness/config.py`, `src/xhtang_harness/cli.py`]
- [ ] Resolve default state, log, artifact, and temp paths from the current worktree unless overridden by external interfaces. [source: `src/xhtang_harness/config.py`; state path implemented for MVP, log/artifact/temp paths deferred]
- [x] Add tests for config precedence, invalid thinking mode, invalid reasoning effort, missing `DEEPSEEK_API_KEY`, and state-path override. [source: `tests/test_config.py`, `tests/test_app.py`, `tests/test_cli.py`]
- [ ] Add tests proving two different working directories resolve different default state/artifact/log paths. [source: `tests/test_parallel_worktree.py`; state path covered, artifact/log paths deferred]

### Phase 2: SQLite Storage

- [x] Implement schema creation with explicit schema versioning. [source: `src/xhtang_harness/storage/sqlite.py`]
- [x] Configure SQLite connection timeout and keep transactions around storage writes only. [source: `src/xhtang_harness/storage/sqlite.py`]
- [ ] Implement session create/open/list helpers. [source: `src/xhtang_harness/storage/sqlite.py`; create/open implemented, list helper deferred]
- [x] Implement run lifecycle helpers: start, complete, fail, cancel. [source: `src/xhtang_harness/storage/sqlite.py`]
- [x] Implement message persistence and history loading in provider-ready order. [source: `src/xhtang_harness/storage/sqlite.py`]
- [x] Implement tool call and provider usage persistence. [source: `src/xhtang_harness/storage/sqlite.py`]
- [x] Add temp SQLite tests for schema creation, run transitions, history replay, and usage storage. [source: `tests/storage/test_sqlite.py`]
- [x] Add a concurrent-storage smoke test with two connections writing separate runs to the same explicit test database. [source: `tests/storage/test_sqlite.py`]

### Phase 3: Tool Registry And Executor

- [x] Define tool schema and executor interfaces independent of DeepSeek SDK objects. [source: `src/xhtang_harness/tools/registry.py`, `src/xhtang_harness/tools/executor.py`]
- [x] Implement built-in `get_current_time` tool with injectable clock. [source: `src/xhtang_harness/tools/builtin.py`]
- [x] Validate tool arguments as JSON before execution. [source: `src/xhtang_harness/tools/executor.py`]
- [ ] Put any tool-created files under the current run artifact directory by default. [source: user follow-up, `doc/external-interfaces.md`]
- [x] Persist tool call start/result/failure states. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/storage/sqlite.py`]
- [x] Add tests for valid tool execution, unknown tool, invalid JSON, and executor exception. [source: `tests/tools/`]

### Phase 4: DeepSeek Provider Adapter

- [ ] Add provider protocol for streaming normalized provider events. [source: `doc/module-responsibilities.md`, `doc/runtime-flow-and-reliability.md`]
- [x] Implement DeepSeek OpenAI-compatible client creation from config. [source: `src/xhtang_harness/app.py`, `src/xhtang_harness/providers/deepseek.py`]
- [x] Map `--thinking` and `--reasoning-effort` to DeepSeek request fields. [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/config.py`, `src/xhtang_harness/providers/deepseek.py`]
- [x] Map tool schemas to DeepSeek `tools` request data. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/tools/registry.py`]
- [ ] Stream `answer_delta` events and keep `reasoning_content` internal by default. [source: `doc/ux-expectations.md`, `.agents/skills/deepseek-api/SKILL.md`]
- [x] Capture usage fields including cache hit and miss tokens. [source: `src/xhtang_harness/providers/deepseek.py`, `src/xhtang_harness/storage/sqlite.py`]
- [x] Classify 400, 401, 402, 422, 429, 500, and 503 errors. [source: `src/xhtang_harness/providers/deepseek.py`]
- [ ] Add fake-client tests for simple answer, streaming chunks, tool-call response, usage mapping, and error classification. [source: `tests/test_deepseek_provider.py`; payload/tool-call/usage/error coverage exists, streaming chunk test deferred]

### Phase 5: Agent Loop

- [x] Implement one-run orchestration from user prompt to final answer. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/app.py`]
- [x] Ensure each provider turn receives full session history. [source: `src/xhtang_harness/agent_loop.py`, `tests/test_agent_loop.py`]
- [x] Preserve assistant `reasoning_content` and `tool_calls` when tool calls occur. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/storage/sqlite.py`, `tests/test_agent_loop.py`]
- [x] Execute tool calls, append tool result messages, and continue until final answer. [source: `src/xhtang_harness/agent_loop.py`, `tests/test_agent_loop.py`]
- [x] Implement bounded retry for retryable provider errors. [source: `src/xhtang_harness/agent_loop.py`]
- [x] Implement cooperative cancellation state that prevents new provider/tool sub-turns. [source: `src/xhtang_harness/agent_loop.py`, `tests/test_agent_loop.py`]
- [ ] Add scripted fake-provider tests for no-tool answer, one-tool loop, retry success, provider failure, tool failure, and cancellation. [source: `tests/test_agent_loop.py`; no-tool/tool-loop/cancellation coverage exists, retry/provider-failure/tool-failure tests deferred]

### Phase 6: CLI Integration

- [x] Replace demo-only CLI output with MVP run command while preserving `--version`. [source: `src/xhtang_harness/cli.py`, shell validation]
- [x] Add command arguments from `doc/external-interfaces.md`: prompt, `--session`, `--thinking`, `--reasoning-effort`, `--stream`, `--no-stream`, `--json`, `--state-path`, and `--debug`. [source: `src/xhtang_harness/cli.py`]
- [x] Display the effective state database path in `--debug` output so parallel worktree runs can verify separation. [source: `src/xhtang_harness/cli.py`]
- [x] Render line-oriented status events and final answer to stdout. [source: `src/xhtang_harness/cli.py`]
- [x] Render command/config errors to stderr and return documented exit codes. [source: `src/xhtang_harness/cli.py`, shell validation]
- [x] Add CLI tests for parser behavior, missing key error, state-path override, and event rendering with fake app service. [source: `tests/test_cli.py`]

### Phase 7: Acceptance, Docs, And Manual Validation

- [x] Update README with MVP setup, required `DEEPSEEK_API_KEY`, example command, state path, and checks. [source: `README.md`]
- [ ] Update `AGENTS.md` if implementation changes canonical commands or module-specific guidance. [source: `AGENTS.md`]
- [x] Run `uv run pytest`. [source: shell validation on 2026-05-30]
- [x] Run `uv run ruff check .`. [source: shell validation on 2026-05-30]
- [x] Run `uv run ruff format --check .`. [source: shell validation on 2026-05-30]
- [x] Run `uv run mypy src`. [source: shell validation on 2026-05-30]
- [ ] Run optional live acceptance with `DEEPSEEK_API_KEY` set: `uv run xhtang-harness --thinking enabled "Use the current time tool and answer with the result."` [source: `doc/mvp.md`, `.agents/skills/deepseek-api/SKILL.md`]
- [ ] Run optional parallel acceptance from two different worktrees or copied checkouts and verify each uses a distinct default `.xhtang-harness/state.sqlite3`. [source: user follow-up]
- [ ] Run optional shared-state acceptance with an explicit `--state-path` and verify runs use distinct run IDs without SQLite lock failures. [source: user follow-up]
- [ ] Verify MVP acceptance checks in `doc/mvp.md`. [source: `doc/mvp.md`]

## Results

- Created this detailed MVP implementation plan at `agents/2026-05-30-mvp-implementation.md`. [source: user request]
- Added parallel worktree separation recommendations covering worktree-local default state, opt-in shared state, collision-resistant run IDs, per-run artifacts, worktree-local logs, short SQLite transactions, and worktree-local temp/config paths. [source: user follow-up, `agents/2026-05-30-mvp-implementation.md`]
- Created source and test skeleton files for app, agent loop, config, conversation, events, errors, telemetry, providers, storage, tools, and parallel-worktree tests. [source: user instruction, code changes]
- Verified current repository checks after skeleton creation: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` pass. [source: shell validation]
- Started MVP implementation from this task document. [source: user instruction on 2026-05-30]
- Implemented the MVP runtime slices for config loading, SQLite persistence, tool registry/execution, agent loop orchestration, CLI event rendering, and README usage. [source: code changes on 2026-05-30]
- Added focused offline tests covering config precedence and worktree-local state, SQLite persistence, built-in tools, tool execution, agent-loop tool replay, cancellation, CLI rendering, and DeepSeek provider mapping. [source: tests changed on 2026-05-30]
- Verified `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` pass. [source: shell validation on 2026-05-30]
- Verified missing API key behavior with `env -u DEEPSEEK_API_KEY uv run xhtang-harness "hello"` returning exit code 2 and a `config_error` message. [source: shell validation on 2026-05-30]
- Verified `uv run xhtang-harness --version` still prints `xhtang-harness 0.1.0`. [source: shell validation on 2026-05-30]
