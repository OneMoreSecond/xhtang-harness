# MVP

## Source Labels

| Label | Source |
| --- | --- |
| Review comment | User review comment on `agents/2026-05-30-init-design.md` |
| Greenfield | `agents/2026-05-30-greenfield.md` |
| UX doc | `doc/ux-expectations.md` |
| Modules doc | `doc/module-responsibilities.md` |
| Storage doc | `doc/persistent-data-storage.md` |
| Runtime doc | `doc/runtime-flow-and-reliability.md` |
| External interfaces doc | `doc/external-interfaces.md` |
| DeepSeek skill | `.agents/skills/deepseek-api/SKILL.md` |
| Design decision | Decision made in this document for the initial implementation plan |

## Terms

| Term | Meaning | Source |
| --- | --- | --- |
| MVP | The smallest implementation that can run a useful local agent loop end to end. | [source: Review comment, Design decision] |
| Runnable | The user can invoke the harness with uv from the checkout and receive a real model-backed answer. | [source: Review comment, Greenfield] |
| Agent loop | Model request, optional tool call, tool result, and final answer loop. | [source: DeepSeek skill, Runtime doc] |
| Required ability | Capability that must exist before the project can be considered a minimal runnable agent harness. | [source: Review comment, Design decision] |

## MVP Goal

The MVP should prove that the harness can accept a local user request, call DeepSeek V4 Pro, stream visible progress, optionally execute a safe local tool, persist the run, and return a final answer without blocking the input surface for the whole run. [source: Review comment, UX doc, DeepSeek skill, Design decision]

## Required Abilities

| Ability | Required behavior | Source |
| --- | --- | --- |
| Local command entry | `uv run xhtang-harness` starts the current checkout without user-wide package installation. | [source: Greenfield] |
| Prompt input | User can pass a prompt by command argument for the first demo. | [source: Greenfield, Design decision] |
| Provider configuration | Harness reads `DEEPSEEK_API_KEY` and optional provider settings from external interfaces. | [source: DeepSeek skill, External interfaces doc] |
| DeepSeek chat call | Harness sends messages to `deepseek-v4-pro` through the OpenAI-compatible API. | [source: DeepSeek skill] |
| Explicit reasoning mode | Harness can run with thinking enabled for agent work and disabled for simple non-reasoning calls. | [source: DeepSeek skill] |
| Streaming event output | Harness emits status and answer events before the full run completes. | [source: UX doc, Runtime doc] |
| Durable session storage | Harness persists sessions, runs, messages, tool calls, and provider usage to SQLite. | [source: Storage doc] |
| Full history replay | Harness sends the complete conversation history on each provider request. | [source: DeepSeek skill, Runtime doc] |
| Tool registry | Harness exposes at least one safe built-in tool through a schema and local executor. | [source: DeepSeek skill, Modules doc, Design decision] |
| Tool-call loop | Harness validates tool arguments, executes the tool, appends tool results, and continues until final answer. | [source: DeepSeek skill, Runtime doc] |
| Reasoning-state preservation | Harness preserves `reasoning_content` when thinking-mode tool calls occur. | [source: DeepSeek skill] |
| Cancellation signal | User can request cancellation; harness records the state and stops starting new work. | [source: UX doc, Runtime doc] |
| Error classification | Harness maps provider/config/tool failures to user-facing error classes and durable run status. | [source: DeepSeek skill, Runtime doc] |

## Minimal Happy Path

1. User runs `uv run xhtang-harness "Use the demo tool and answer my request"`. [source: Greenfield, Design decision]
2. CLI creates or opens a local session and records a run. [source: Storage doc]
3. Runtime emits `run_started`. [source: UX doc, Runtime doc]
4. DeepSeek provider streams model output or tool calls. [source: DeepSeek skill, Runtime doc]
5. Tool executor runs one safe tool if requested. [source: Modules doc, Runtime doc]
6. Runtime appends tool results and continues the provider loop. [source: DeepSeek skill, Runtime doc]
7. Final answer is printed and persisted with usage metadata. [source: Storage doc, Runtime doc]

## MVP Deferrals

| Deferred ability | Reason | Source |
| --- | --- | --- |
| Rich TUI or web UI | The MVP can prove responsiveness with event lines in the CLI first. | [source: UX doc, Design decision] |
| Multiple providers | DeepSeek V4 Pro is the planned primary provider. | [source: DeepSeek skill, Design decision] |
| Hosted multi-user storage | Local SQLite is enough for the first runnable harness. | [source: Storage doc] |
| Complex tool permission UI | Start with a small allowlisted tool registry. | [source: Modules doc, Design decision] |
| Conversation export/delete commands | Important before broad use, but not required for the first runnable loop. | [source: Storage doc] |
| Background run queue across processes | A single active run is enough for the first demo. | [source: UX doc, Design decision] |

## MVP Acceptance Checks

| Check | Pass condition | Source |
| --- | --- | --- |
| Local command | Running `uv run xhtang-harness "hello"` starts without user-wide installation. | [source: Greenfield] |
| Missing API key | Missing `DEEPSEEK_API_KEY` returns a clear configuration error. | [source: DeepSeek skill, Design decision] |
| Provider call | With a valid key, the harness receives a DeepSeek answer. | [source: DeepSeek skill] |
| Stream behavior | User sees at least start, progress, and final events during a run. | [source: UX doc] |
| Persistence | A completed run can be listed or inspected from SQLite. | [source: Storage doc] |
| Tool loop | A model-requested safe tool call completes and feeds back into the final answer. | [source: DeepSeek skill, Runtime doc] |
| Cancellation | Cancellation changes durable run status and prevents further tool/provider sub-turns. | [source: Runtime doc] |
