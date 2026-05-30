# Usage

Use `xhtang-harness` from this repository or a git worktree. [source: `src/xhtang_harness/cli.py`, `pyproject.toml`]

## Source Labels

| Label | Source |
| --- | --- |
| CLI | `src/xhtang_harness/cli.py` |
| Config | `src/xhtang_harness/config.py` |
| App | `src/xhtang_harness/app.py` |
| Agent loop | `src/xhtang_harness/agent_loop.py` |
| Events | `src/xhtang_harness/events.py` |
| Tools | `src/xhtang_harness/tools/builtin.py` |
| Skills | `src/xhtang_harness/skills.py` |
| Storage | `src/xhtang_harness/storage/sqlite.py` |
| Project | `pyproject.toml`, `.python-version` |
| DeepSeek | `.agents/skills/deepseek-api/SKILL.md` |
| Tests | `tests/test_cli.py`, `tests/test_config.py`, `tests/test_agent_loop.py` |

## Requirements

| Requirement | Detail | Source |
| --- | --- | --- |
| `uv` | Runs setup, CLI commands, and checks. | [source: Project] |
| Python 3.12 | Project Python version selected by uv. | [source: Project] |
| `DEEPSEEK_API_KEY` | Required for real provider-backed prompts. | [source: App, Config] |

## Setup

Create or refresh the local environment: [source: Project]

```bash
uv sync
```

Set the DeepSeek API key for provider calls: [source: App, Config, DeepSeek]

```bash
export DEEPSEEK_API_KEY="..."
```

## Minimal Run

Run a simple provider-backed prompt: [source: CLI, App]

```bash
uv run xhtang-harness "Reply with one short sentence: hello from xhtang-harness."
```

The CLI prints line-oriented events such as `run_started`, `message_recorded`, `provider_request_started`, `answer_delta`, and `run_completed`. Exact answer text is model output. [source: CLI, Events, Agent loop]

Use the current-time tool when you want a minimal tool example: [source: Tools, Agent loop]

```bash
uv run xhtang-harness "Use the get_current_time tool, then tell me the UTC time."
```

## Explicit Local File Changes

The harness exposes a `bash` tool. It should inspect local state by default and make changes only when the user explicitly asks for local file changes. [source: Tools]

Example file-writing prompt: [source: Tools]

```bash
uv run xhtang-harness \
  "Use the bash tool to create fibonacci_first_30.py in the current directory. The script should calculate and print the first 30 Fibonacci numbers."
```

After a successful file-writing run, inspect the generated file yourself before using it: [source: Tools]

```bash
uv run python fibonacci_first_30.py
```

## Local Skills

The harness reads local skills from `.skills/<skill-name>/SKILL.md` by default. A skill matches when the prompt contains the skill `name` or exact `description`; the matched skill body is sent to the provider as a system instruction for that run. [source: Config, Skills, Tests]

Example skill file: [source: Skills]

```markdown
---
name: example-skill
description: Use when the prompt mentions example-skill.
---

Follow these reusable instructions.
```

Enable post-run skill reflection when you want the harness to ask whether a completed successful run deserves a reusable skill: [source: Agent loop, Skills]

```bash
uv run xhtang-harness --skill-learning suggest "Summarize this workflow."
uv run xhtang-harness --skill-learning auto "Summarize this workflow."
```

`suggest` prints and persists the proposal without writing skill files. `auto` writes validated skills under `.skills/` when the model returns `should_create: true`. [source: Agent loop, Skills]

## Built-In Tools

| Tool | Purpose | Source |
| --- | --- | --- |
| `get_current_time` | Returns the current UTC time as an ISO-8601 timestamp. | [source: Tools] |
| `bash` | Runs `/bin/bash -lc` with captured exit code, stdout, stderr, optional `cwd`, and a bounded timeout. | [source: Tools] |

## Options

| Option | Description | Source |
| --- | --- | --- |
| `goal` | Prompt describing what you want the harness to do. | [source: CLI, Config] |
| `--session <id>` | Continue or create a specific local session. | [source: CLI, Storage] |
| `--thinking enabled\|disabled` | Select DeepSeek thinking mode. | [source: CLI, Config, DeepSeek] |
| `--reasoning-effort high\|max` | Select reasoning effort when thinking is enabled. | [source: CLI, Config, DeepSeek] |
| `--stream` / `--no-stream` | Sets the stream preference in config. Current CLI output still renders `answer_delta` events, so `--no-stream` is not a full quiet mode yet. | [source: CLI, Tests] |
| `--json` | Request JSON provider output and render event lines as JSON. Include the word `json` in the prompt for DeepSeek JSON mode. | [source: CLI, Agent loop, DeepSeek] |
| `--state-path <path>` | Override the SQLite state database path. | [source: CLI, Config, Storage] |
| `--skill-learning off\|suggest\|auto` | Control post-run skill reflection. Defaults to `off`. | [source: CLI, Config, Agent loop] |
| `--skills-path <path>` | Override the local skill directory. Defaults to `.skills` under the current worktree. | [source: CLI, Config, Skills] |
| `--debug` | Print local runtime details such as the effective state path. | [source: CLI] |
| `--version` | Print the package version and exit. | [source: CLI, Project] |

## Environment Variables

| Variable | Purpose | Source |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | API key for real provider calls. | [source: App, Config, DeepSeek] |
| `DEEPSEEK_BASE_URL` | Override the OpenAI-compatible DeepSeek base URL. | [source: Config, DeepSeek] |
| `DEEPSEEK_MODEL` | Override the provider model. The default is `deepseek-v4-pro`. | [source: Config, DeepSeek] |
| `XHTANG_HARNESS_THINKING` | Default thinking mode when no CLI value is provided. | [source: Config] |
| `XHTANG_HARNESS_REASONING_EFFORT` | Default reasoning effort when no CLI value is provided. | [source: Config] |
| `XHTANG_HARNESS_STATE_PATH` | Default SQLite state path when no CLI value is provided. | [source: Config] |
| `XHTANG_HARNESS_SKILL_LEARNING` | Default skill-learning mode when no CLI value is provided. | [source: Config] |
| `XHTANG_HARNESS_SKILLS_PATH` | Default local skill directory when no CLI value is provided. | [source: Config] |
| `XHTANG_HARNESS_USER_ID` | Optional non-private user isolation ID passed to DeepSeek. | [source: Config, DeepSeek] |

Do not put API keys or private personal data in skill files, `XHTANG_HARNESS_USER_ID`, or `.xhtang-harness/config.toml`. [source: DeepSeek, Config, Skills]

## Local Files

| Path | Purpose | Source |
| --- | --- | --- |
| `.xhtang-harness/config.toml` | Optional local config. CLI args override environment variables, environment variables override this file, and this file overrides code defaults. | [source: Config] |
| `.xhtang-harness/state.sqlite3` | Default SQLite state database under the current worktree. | [source: Config, Storage] |
| `.skills/<skill-name>/SKILL.md` | Default local skill file path. | [source: Config, Skills] |

Default state and skill paths are worktree-local. Use explicit `--state-path`, `XHTANG_HARNESS_STATE_PATH`, `--skills-path`, or `XHTANG_HARNESS_SKILLS_PATH` when you intentionally want a shared path. [source: Config, Tests]

Example local config: [source: Config]

```toml
thinking = "enabled"
reasoning_effort = "high"
state_path = ".xhtang-harness/state.sqlite3"
skill_learning = "off"
skills_path = ".skills"
model = "deepseek-v4-pro"
```

## Checks

Run checks from the repository root: [source: Project]

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Troubleshooting

| Problem | What to do | Source |
| --- | --- | --- |
| `uv` is not found | Install `uv`, then run `uv sync` from the repository root. | [source: Project] |
| Missing API key | Set `DEEPSEEK_API_KEY` before running provider-backed prompts. | [source: App, Config] |
| Python version error | Run `uv sync` from the repository root so uv can use the project Python version. | [source: Project] |
| Empty prompt error | Pass a non-empty prompt. | [source: Config] |
| Command is not found | Run it through uv: `uv run xhtang-harness`. | [source: Project, CLI] |
| `--no-stream` still prints an answer line | Current CLI rendering still emits `answer_delta` lines; treat `--no-stream` as a stored preference, not a complete quiet mode. | [source: CLI, Tests] |
| JSON output is empty or invalid | Include the word `json` in the prompt, provide a concrete schema or example, and keep the requested output small enough to fit. | [source: DeepSeek] |
| Skill was not used | Make sure the prompt includes the skill `name` or exact `description`, and that the skill file has valid frontmatter plus a non-empty body. | [source: Skills, Tests] |
| Skill learning did not write files | Use `--skill-learning auto`; `suggest` only emits a proposal. Existing skill directories are not overwritten. | [source: Agent loop, Skills] |
| State appears missing in another worktree | Default state is worktree-local. Pass the same explicit state path only when shared history is intended. | [source: Config, Tests] |
