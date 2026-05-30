# UX Expectations

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
| Run | One user request processed by the harness until final answer, cancellation, or failure. | [source: Design decision] |
| Event | A typed update emitted while a run is active, such as status, token, tool call, or error. | [source: Design decision, DeepSeek skill] |
| Responsive input | The user can still type, cancel, or queue the next action while a run is in progress. | [source: User task] |
| Final answer | The user-facing answer text produced after provider reasoning and tool calls finish. | [source: DeepSeek skill] |
| Reasoning content | Provider-side thinking state returned separately from final answer content. | [source: DeepSeek skill] |

## Product Goal

The first harness UX should make long-running model and tool work visible, interruptible, and resumable from the uv-run local command entry. [source: User task, Greenfield, Design decision]

## Expectations

| Expectation | Initial design | Source |
| --- | --- | --- |
| The user is not blocked by a long provider call. | Run model and tool work in a background execution path while the input surface stays available for cancel or next input. | [source: User task, Design decision] |
| The user sees immediate acknowledgement. | Emit a local `run_started` event before any network call. | [source: User task, Design decision] |
| The user sees progress during long work. | Stream provider tokens, tool-call status, retry notices, and final status events. | [source: User task, DeepSeek skill, Design decision] |
| The user can cancel. | Accept cancel input and mark the run as `cancel_requested`; stop launching new tool calls after cancellation is recorded. | [source: User task, Design decision] |
| The user can recover after failure. | Persist the failed run and display a short error with a retryable/non-retryable classification. | [source: DeepSeek skill, Design decision] |
| Reasoning is not exposed by default. | Store provider `reasoning_content` only when needed for tool-call continuity and internal debugging. | [source: DeepSeek skill, Design decision] |
| Tool calls are understandable. | Show tool name, pending/running/succeeded/failed state, and a compact summary of tool result. | [source: DeepSeek skill, Design decision] |
| The same session can continue later. | Store sessions, messages, runs, and tool results in the persistent store. | [source: User task, Design decision] |

## Interaction States

| State | User-visible behavior | Implementation note | Source |
| --- | --- | --- | --- |
| Idle | Prompt accepts input. | No active run is attached to the input surface. | [source: Design decision] |
| Submitting | Prompt remains visible and shows that the request was accepted. | Create a run record before provider work begins. | [source: User task, Design decision] |
| Streaming | Output grows incrementally and input remains usable. | Render events as they arrive. | [source: User task, DeepSeek skill, Design decision] |
| Tool running | UI shows the current tool name and status. | Tool executor emits events around each tool call. | [source: DeepSeek skill, Design decision] |
| Waiting retry | UI shows retry countdown or retry reason. | Retry policy emits a status event before sleeping. | [source: DeepSeek skill, Design decision] |
| Cancel requested | UI shows cancellation is pending. | Cancellation is cooperative because provider and tool calls may already be in flight. | [source: User task, Design decision] |
| Complete | Final answer is visible and stored. | Persist final assistant message and usage metadata. | [source: DeepSeek skill, Design decision] |
| Failed | Error is visible with next action. | Persist error class and raw diagnostic detail separately. | [source: DeepSeek skill, Design decision] |

## First Demo Scope

| In scope | Out of scope | Source |
| --- | --- | --- |
| `uv run xhtang-harness` CLI command. | Multi-user web application. | [source: Greenfield, Design decision] |
| Streaming text and status events. | Rich terminal layout with panes and mouse interactions. | [source: User task, Design decision] |
| Session persistence in local storage. | Hosted database or cloud sync. | [source: User task, Design decision] |
| DeepSeek V4 Pro provider path. | Multiple provider selection UI. | [source: DeepSeek skill, Design decision] |
| Cancel and retry semantics. | Hard process termination guarantees for every external tool. | [source: User task, Design decision] |
