# Persistent Data Storage

## Source Labels

| Label | Source |
| --- | --- |
| User task | `agents/2026-05-30-init-design.md` |
| Greenfield | `agents/2026-05-30-greenfield.md` |
| DeepSeek skill | `.agents/skills/deepseek-api/SKILL.md` |
| Python stdlib | Python 3.12 standard library availability of `sqlite3` |
| Design decision | Decision made in this document for the initial implementation plan |

## Terms

| Term | Meaning | Source |
| --- | --- | --- |
| SQLite | Local embedded SQL database available through Python standard library `sqlite3`. | [source: Python stdlib] |
| Session | Durable conversation container that can hold many user turns and runs. | [source: User task, Design decision] |
| Run | One attempt to answer a user request. | [source: Design decision] |
| Message | A persisted user, assistant, system, or tool message. | [source: DeepSeek skill, Design decision] |
| Usage | Provider token and cache accounting returned by the model API. | [source: DeepSeek skill] |

## Storage Decision

Use SQLite as the first persistent store for the local harness. [source: User task, Python stdlib, Design decision]

| Reason | Detail | Source |
| --- | --- | --- |
| No new runtime dependency | Python includes `sqlite3`, which fits the current small Python scaffold. | [source: Greenfield, Python stdlib, Design decision] |
| Transactional writes | Sessions, messages, tool calls, and run status should commit atomically. | [source: User task, Design decision] |
| Queryable history | Users and tests need to inspect prior sessions and failed runs. | [source: User task, Design decision] |
| Local-first scope | The first demo does not require hosted multi-user storage. | [source: Greenfield, Design decision] |

## Storage Location

| Setting | Default | Source |
| --- | --- | --- |
| Database path | `.xhtang-harness/state.sqlite3` under the current working tree. | [source: Design decision] |
| Override | `XHTANG_HARNESS_STATE_PATH`. | [source: Design decision] |
| Directory policy | Create the parent directory on first write. | [source: Design decision] |
| Git policy | Keep `.xhtang-harness/` ignored. | [source: Design decision] |

## Schema Draft

| Table | Purpose | Important fields | Source |
| --- | --- | --- | --- |
| `sessions` | Store conversation containers. | `id`, `title`, `created_at`, `updated_at`, `status` | [source: User task, Design decision] |
| `runs` | Store one model/tool execution attempt. | `id`, `session_id`, `status`, `started_at`, `ended_at`, `error_code`, `error_message` | [source: User task, DeepSeek skill, Design decision] |
| `messages` | Store user, assistant, system, and tool messages. | `id`, `session_id`, `run_id`, `role`, `content`, `reasoning_content`, `tool_call_id`, `created_at` | [source: DeepSeek skill, Design decision] |
| `tool_calls` | Store tool requests and results. | `id`, `run_id`, `provider_tool_call_id`, `name`, `arguments_json`, `result_text`, `status`, `error_message` | [source: DeepSeek skill, Design decision] |
| `provider_usage` | Store provider token and cache telemetry. | `run_id`, `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens` | [source: DeepSeek skill] |
| `events` | Store optional replayable event stream. | `id`, `run_id`, `type`, `payload_json`, `created_at` | [source: User task, Design decision] |

## Write Policy

| Operation | Policy | Source |
| --- | --- | --- |
| Start run | Insert `runs` row before the provider request starts. | [source: User task, Design decision] |
| Stream token | Emit to UI immediately; persist as event only if replay is enabled. | [source: User task, Design decision] |
| Assistant message | Persist final assistant message after the provider turn completes. | [source: DeepSeek skill, Design decision] |
| Tool call | Persist tool call request before executing the local tool. | [source: DeepSeek skill, Design decision] |
| Tool result | Persist result or error before the next provider request. | [source: DeepSeek skill, Design decision] |
| Usage | Persist token and cache fields after each provider response. | [source: DeepSeek skill] |
| Failure | Persist error class and user-facing message; keep raw diagnostic detail out of normal output. | [source: DeepSeek skill, Design decision] |

## Privacy And Retention

| Rule | Detail | Source |
| --- | --- | --- |
| Do not store API keys. | API keys belong in environment variables or external secret storage. | [source: DeepSeek skill, Design decision] |
| Do not put private data in `user_id`. | DeepSeek guidance says `user_id` should not contain user privacy information. | [source: DeepSeek skill] |
| Store reasoning content only when useful. | Keep `reasoning_content` for tool-call continuity and debugging, not default user display. | [source: DeepSeek skill, Design decision] |
| Add export/delete commands later. | Users need control over local conversation history before broader usage. | [source: Design decision] |
