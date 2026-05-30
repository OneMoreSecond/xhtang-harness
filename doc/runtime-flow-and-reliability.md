# Runtime Flow And Reliability

## Source Labels

| Label | Source |
| --- | --- |
| User task | `agents/2026-05-30-init-design.md` |
| Greenfield | `agents/2026-05-30-greenfield.md` |
| DeepSeek skill | `.agents/skills/deepseek-api/SKILL.md` |
| UX doc | `doc/ux-expectations.md` |
| Storage doc | `doc/persistent-data-storage.md` |
| Design decision | Decision made in this document for the initial implementation plan |

## Terms

| Term | Meaning | Source |
| --- | --- | --- |
| Event stream | Ordered runtime updates consumed by the UI and optionally persisted. | [source: UX doc, Design decision] |
| Provider turn | One DeepSeek API call and its response stream. | [source: DeepSeek skill, Design decision] |
| Tool sub-turn | One model-requested tool execution followed by a tool result message. | [source: DeepSeek skill, Design decision] |
| Retryable failure | Error where retry can be useful, such as HTTP 429, 500, or 503. | [source: DeepSeek skill] |
| Cooperative cancellation | Cancellation state that prevents new work and asks active work to stop when the boundary supports it. | [source: User task, Design decision] |

## Run Flow

| Step | Action | Event examples | Source |
| --- | --- | --- | --- |
| 1 | Create a run record and emit start. | `run_started` | [source: User task, Storage doc, Design decision] |
| 2 | Load session history and append the user message. | `message_recorded` | [source: DeepSeek skill, Storage doc] |
| 3 | Call DeepSeek with explicit thinking mode and `user_id` when configured. | `provider_request_started` | [source: DeepSeek skill] |
| 4 | Stream answer deltas and status updates. | `answer_delta`, `reasoning_delta_internal` | [source: DeepSeek skill, UX doc] |
| 5 | If tool calls are returned, persist assistant state and execute tools. | `tool_call_started`, `tool_call_finished` | [source: DeepSeek skill, Storage doc] |
| 6 | Append tool result messages and call the provider again. | `provider_request_started` | [source: DeepSeek skill] |
| 7 | Persist final assistant message and usage telemetry. | `run_completed` | [source: DeepSeek skill, Storage doc] |
| 8 | On error, classify, persist, and emit a user-facing message. | `run_failed` | [source: DeepSeek skill, Storage doc] |

## Responsiveness Model

The UI should consume events from a run queue rather than block on the final provider response. [source: User task, UX doc, Design decision]

| Concern | Design | Source |
| --- | --- | --- |
| Long provider latency | Emit start and retry events before waiting on network or backoff. | [source: User task, DeepSeek skill, Design decision] |
| Streaming answer | Render answer deltas as they arrive. | [source: DeepSeek skill, UX doc] |
| User input during run | Keep input surface active and map cancel input to run cancellation state. | [source: User task, UX doc] |
| Tool latency | Emit tool status events around each tool execution. | [source: DeepSeek skill, UX doc] |
| Resume after crash | Persist run status and messages before external side effects where practical. | [source: Storage doc, Design decision] |

## Cancellation

| Rule | Detail | Source |
| --- | --- | --- |
| Cancellation is explicit state. | Store `cancel_requested` before stopping new work. | [source: User task, Storage doc, Design decision] |
| Provider cancellation is best effort. | Active HTTP requests may not stop immediately in every client implementation. | [source: Design decision] |
| Tool cancellation is tool-specific. | Tools should expose cancellable boundaries when they do long work. | [source: Design decision] |
| Final state is durable. | Mark the run `cancelled` if no final answer should be shown. | [source: User task, Storage doc, Design decision] |

## Retry Policy

| Error | Policy | Source |
| --- | --- | --- |
| 400 | Do not retry by default; inspect request shape and reasoning/tool-call history. | [source: DeepSeek skill] |
| 401 | Do not retry; report API key configuration failure. | [source: DeepSeek skill] |
| 402 | Do not retry; report balance or billing problem. | [source: DeepSeek skill] |
| 422 | Do not retry; report invalid parameter failure. | [source: DeepSeek skill] |
| 429 | Retry with bounded exponential backoff and reduce concurrency. | [source: DeepSeek skill] |
| 500 | Retry with bounded exponential backoff. | [source: DeepSeek skill] |
| 503 | Retry with bounded exponential backoff and show provider-busy status. | [source: DeepSeek skill] |

## Provider-Specific State

| State | Harness rule | Source |
| --- | --- | --- |
| `reasoning_content` | Preserve when tool calls occur; do not show to users by default. | [source: DeepSeek skill] |
| `tool_calls` | Persist and replay assistant tool-call messages before tool result messages. | [source: DeepSeek skill, Storage doc] |
| `finish_reason=tool_calls` | Continue the tool loop. | [source: DeepSeek skill] |
| `finish_reason=length` | Mark incomplete and suggest increasing max output or compacting context. | [source: DeepSeek skill, Design decision] |
| Cache telemetry | Record hit and miss token counts for cost visibility. | [source: DeepSeek skill, Storage doc] |
