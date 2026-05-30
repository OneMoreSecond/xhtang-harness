# Module Responsibilities

## Source Labels

| Label | Source |
| --- | --- |
| User task | `agents/2026-05-30-init-design.md` |
| Greenfield | `agents/2026-05-30-greenfield.md` |
| CLI code | `src/xhtang_harness/cli.py`, `pyproject.toml`, and `README.md` |
| DeepSeek skill | `.agents/skills/deepseek-api/SKILL.md` |
| Design decision | Decision made in this document for the initial implementation plan |

## Terms

| Term | Meaning | Source |
| --- | --- | --- |
| Boundary | A module responsibility line that other modules should not cross directly. | [source: Design decision] |
| Provider adapter | Code that translates harness requests into a vendor API call and translates responses into harness events. | [source: DeepSeek skill, Design decision] |
| Agent loop | Runtime loop that calls the provider, handles tool calls, appends messages, and ends with final output. | [source: DeepSeek skill, Design decision] |
| Tool registry | Local catalog of callable tools and their schemas. | [source: DeepSeek skill, Design decision] |
| Storage gateway | Module that owns durable reads and writes. | [source: User task, Design decision] |

## Responsibility Map

| Module | Responsibility | Must not own | Source |
| --- | --- | --- | --- |
| `xhtang_harness.cli` | Parse command-line input, select session, render events, and call application services. | Provider-specific request construction or direct database SQL. | [source: CLI code, Design decision] |
| `xhtang_harness.app` | Coordinate user commands, sessions, runs, storage, and agent loop dependencies. | DeepSeek API details or tool implementation logic. | [source: User task, Design decision] |
| `xhtang_harness.conversation` | Define message, session, run, and event data structures. | Persistence backend choices. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.agent_loop` | Execute the provider/tool loop and emit events until final answer, failure, or cancellation. | Terminal rendering or direct environment variable parsing. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.providers.deepseek` | Build DeepSeek requests, handle streaming chunks, preserve `reasoning_content`, classify provider errors, and expose usage metadata. | User interface state or storage schema migrations. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.tools.registry` | Register tool schemas and map tool names to local executors. | Provider retry policy. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.tools.executor` | Validate tool arguments, run approved tools, and return tool-result events. | Conversation rendering. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.storage.sqlite` | Persist sessions, messages, runs, tool calls, and provider usage in SQLite. | Provider API calls or UI formatting. | [source: User task, Design decision] |
| `xhtang_harness.config` | Load environment and local configuration such as API keys, storage path, and provider defaults. | Network calls or SQL writes. | [source: DeepSeek skill, Design decision] |
| `xhtang_harness.telemetry` | Emit structured logs and metrics for latency, retries, cache hit tokens, and failures. | Business decisions about retry or cancellation. | [source: DeepSeek skill, Design decision] |

## Initial Package Shape

```text
src/xhtang_harness/
  cli.py
  app.py
  conversation.py
  agent_loop.py
  config.py
  telemetry.py
  providers/
    deepseek.py
  storage/
    sqlite.py
  tools/
    registry.py
    executor.py
```

This shape is a design target for later implementation, not current code state. [source: CLI code, Design decision]

## Interface Rules

| Rule | Rationale | Source |
| --- | --- | --- |
| UI consumes events instead of provider SDK objects. | This keeps CLI, TUI, and future web views independent from provider internals. | [source: User task, DeepSeek skill, Design decision] |
| Provider adapter receives normalized messages and options. | This keeps DeepSeek-specific parameters such as `thinking` and `reasoning_effort` behind one boundary. | [source: DeepSeek skill, Design decision] |
| Agent loop appends assistant messages before tool-result messages. | DeepSeek tool-call continuation requires preserving assistant tool-call state. | [source: DeepSeek skill] |
| Storage writes run status transitions explicitly. | Durable run state supports resume, retry, and post-failure inspection. | [source: User task, Design decision] |
| Tool executor validates model-generated JSON arguments before execution. | DeepSeek docs warn that generated tool arguments may be invalid or contain hallucinated fields. | [source: DeepSeek skill] |
