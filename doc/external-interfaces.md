# External Interfaces

## Source Labels

| Label | Source |
| --- | --- |
| Review comment | User review comment on `agents/2026-05-30-init-design.md` |
| Greenfield | `agents/2026-05-30-greenfield.md` |
| README | `README.md` |
| UX doc | `doc/ux-expectations.md` |
| Modules doc | `doc/module-responsibilities.md` |
| Storage doc | `doc/persistent-data-storage.md` |
| Runtime doc | `doc/runtime-flow-and-reliability.md` |
| DeepSeek skill | `.agents/skills/deepseek-api/SKILL.md` |
| Design decision | Decision made in this document for the initial implementation plan |

## Terms

| Term | Meaning | Source |
| --- | --- | --- |
| External interface | Any input or output boundary outside in-memory Python objects. | [source: Review comment, Design decision] |
| Read source | Disk file, command argument, or environment variable read by the harness. | [source: Review comment] |
| Output file | File or database the harness creates or mutates. | [source: Review comment, Storage doc] |
| User state | User-controllable state that affects a run, session, provider call, tool behavior, or output location. | [source: Review comment, Design decision] |

## Command Arguments

| User state | Argument | Required | Consumer | Source |
| --- | --- | --- | --- | --- |
| Prompt text | Positional `goal` or future `prompt` argument | Yes for non-interactive run | `xhtang_harness.cli` | [source: Greenfield, Design decision] |
| Session selector | `--session <id-or-name>` | No | `xhtang_harness.cli`, `xhtang_harness.app` | [source: Storage doc, Design decision] |
| Thinking mode | `--thinking enabled|disabled` | No | `xhtang_harness.providers.deepseek` | [source: DeepSeek skill, Design decision] |
| Reasoning effort | `--reasoning-effort high|max` | No | `xhtang_harness.providers.deepseek` | [source: DeepSeek skill, Design decision] |
| Stream output | `--stream` / `--no-stream` | No | `xhtang_harness.cli`, agent loop | [source: UX doc, Runtime doc] |
| JSON output request | `--json` | No | Provider options and prompt builder | [source: DeepSeek skill, Design decision] |
| Storage path | `--state-path <path>` | No | `xhtang_harness.storage.sqlite` | [source: Storage doc, Design decision] |
| Debug mode | `--debug` | No | CLI, telemetry, provider adapter | [source: Runtime doc, Design decision] |

## Environment Variables

| User state | Environment variable | Required | Consumer | Source |
| --- | --- | --- | --- | --- |
| DeepSeek API key | `DEEPSEEK_API_KEY` | Yes for real provider calls | `xhtang_harness.config`, DeepSeek provider | [source: DeepSeek skill] |
| DeepSeek base URL | `DEEPSEEK_BASE_URL` | No | DeepSeek provider | [source: DeepSeek skill, Design decision] |
| DeepSeek model | `DEEPSEEK_MODEL` | No | DeepSeek provider | [source: DeepSeek skill, Design decision] |
| Default thinking mode | `XHTANG_HARNESS_THINKING` | No | Config and provider options | [source: DeepSeek skill, Design decision] |
| Default reasoning effort | `XHTANG_HARNESS_REASONING_EFFORT` | No | Config and provider options | [source: DeepSeek skill, Design decision] |
| State database path | `XHTANG_HARNESS_STATE_PATH` | No | SQLite storage | [source: Storage doc] |
| Log level | `XHTANG_HARNESS_LOG_LEVEL` | No | Telemetry | [source: Runtime doc, Design decision] |
| User isolation ID | `XHTANG_HARNESS_USER_ID` | No | DeepSeek provider `user_id` | [source: DeepSeek skill, Design decision] |

## Disk Inputs

| User state | Disk path | Required | Reader | Source |
| --- | --- | --- | --- | --- |
| Local config | `.xhtang-harness/config.toml` | No | `xhtang_harness.config` | [source: Design decision] |
| Persistent state | `.xhtang-harness/state.sqlite3` or override path | No on first run; yes for resume/list | `xhtang_harness.storage.sqlite` | [source: Storage doc] |
| Tool definitions | Future `.xhtang-harness/tools/*.toml` | No | Tool registry | [source: Modules doc, Design decision] |
| Prompt templates | Future `.xhtang-harness/prompts/*.md` | No | Prompt builder | [source: Design decision] |

Configuration precedence should be command argument, then environment variable, then disk config, then code default. [source: Design decision]

## Output Files

| Output | Path | Writer | Purpose | Source |
| --- | --- | --- | --- | --- |
| State database | `.xhtang-harness/state.sqlite3` or `XHTANG_HARNESS_STATE_PATH` | SQLite storage | Sessions, runs, messages, tool calls, events, and provider usage. | [source: Storage doc] |
| State directory | `.xhtang-harness/` | Storage/config modules | Parent directory for local runtime state. | [source: Storage doc] |
| Log file | `.xhtang-harness/logs/harness.log` | Telemetry | Local diagnostics when file logging is enabled. | [source: Runtime doc, Design decision] |
| Exported session | User-specified path from future `export` command | CLI/app | Portable transcript export. | [source: Storage doc, Design decision] |
| Tool artifacts | `.xhtang-harness/artifacts/<run-id>/` | Tool executor | Files created by tools during a run. | [source: Runtime doc, Design decision] |

## Non-File Outputs

| Output | Destination | Source |
| --- | --- | --- |
| Answer and status events | `stdout` | [source: UX doc, Runtime doc] |
| User-facing errors | `stderr` for command-level failures; event stream for run-level failures | [source: Runtime doc, Design decision] |
| Process exit code | Shell caller | [source: Greenfield, Design decision] |

## Interface Rules

| Rule | Rationale | Source |
| --- | --- | --- |
| Never write API keys to disk. | Prevent accidental credential persistence. | [source: DeepSeek skill, Design decision] |
| Keep `user_id` non-private. | DeepSeek docs warn not to include private user data in `user_id`. | [source: DeepSeek skill] |
| Keep generated runtime files under `.xhtang-harness/` unless the user gives an output path. | Makes cleanup and git ignore behavior predictable. | [source: Storage doc, Design decision] |
| Validate disk config before starting a run. | Configuration errors should fail before network calls or tool side effects. | [source: Runtime doc, Design decision] |
| Print machine-readable output only when explicitly requested. | Normal CLI output should remain human-readable. | [source: UX doc, Design decision] |
