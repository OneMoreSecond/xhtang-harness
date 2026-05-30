# Usage

Use `xhtang-harness` from this repository or a git worktree.

## Requirements

- `uv`
- Python 3.12
- `DEEPSEEK_API_KEY` for real DeepSeek-backed prompts

## Setup

Create or refresh the local environment:

```bash
uv sync
```

Set your DeepSeek API key:

```bash
export DEEPSEEK_API_KEY="..."
```

## Minimal Run

Run a simple prompt:

```bash
uv run xhtang-harness "Reply with one short sentence: hello from xhtang-harness."
```

The command prints line-oriented progress events and the model answer.

Use the current-time tool for a small tool example:

```bash
uv run xhtang-harness "Use the get_current_time tool, then tell me the UTC time."
```

## Explicit Local File Changes

The harness can use a local `bash` tool. It should inspect local state by
default and make changes only when you explicitly ask for local file changes.

Example file-writing prompt:

```bash
uv run xhtang-harness \
  "Use the bash tool to create fibonacci_first_30.py in the current directory. The script should calculate and print the first 30 Fibonacci numbers."
```

After a successful file-writing run, inspect the generated file before using
it:

```bash
uv run python fibonacci_first_30.py
```

## Skills

The harness can load local skills from `.skills/<skill-name>/SKILL.md`.

Enable post-run skill reflection when you want the harness to suggest or create
a reusable skill from a successful run:

```bash
uv run xhtang-harness --skill-learning suggest "Summarize this workflow."
uv run xhtang-harness --skill-learning auto "Summarize this workflow."
```

`suggest` prints and persists a proposal without writing skill files. `auto`
writes validated skills under `.skills/` when a reusable workflow is found.

## Options

| Option | Description |
| --- | --- |
| `goal` | Initial prompt describing what you want the harness to do. If omitted, the CLI asks for it before beginning. Blank prompts are rejected. |
| `--session <id>` | Continue or create a specific local session. |
| `--thinking enabled\|disabled` | Select DeepSeek thinking mode. |
| `--reasoning-effort high\|max` | Select reasoning effort when thinking is enabled. |
| `--stream` / `--no-stream` | Set the stream preference. This version still prints answer event lines. |
| `--json` | Request JSON model output and render events as JSON lines. Include the word `json` in the prompt. |
| `--state-path <path>` | Override the local state database path. |
| `--skill-learning off\|suggest\|auto` | Control post-run skill reflection. |
| `--skills-path <path>` | Override the local skill directory. |
| `--debug` | Print local runtime details such as the effective state path. |
| `--version` | Print the package version and exit. |

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `DEEPSEEK_API_KEY` | API key for real DeepSeek calls. |
| `DEEPSEEK_BASE_URL` | Override the OpenAI-compatible DeepSeek base URL. |
| `DEEPSEEK_MODEL` | Override the DeepSeek model. |
| `XHTANG_HARNESS_THINKING` | Default thinking mode when no CLI value is provided. |
| `XHTANG_HARNESS_REASONING_EFFORT` | Default reasoning effort when no CLI value is provided. |
| `XHTANG_HARNESS_STATE_PATH` | Default local state path when no CLI value is provided. |
| `XHTANG_HARNESS_SKILL_LEARNING` | Default skill-learning mode when no CLI value is provided. |
| `XHTANG_HARNESS_SKILLS_PATH` | Default local skill directory when no CLI value is provided. |
| `XHTANG_HARNESS_USER_ID` | Optional non-private user isolation ID passed to DeepSeek. |

Do not put API keys or private personal data in skill files,
`XHTANG_HARNESS_USER_ID`, or `.xhtang-harness/config.toml`.

## Local Files

| Path | Purpose |
| --- | --- |
| `.xhtang-harness/config.toml` | Optional local config. CLI args override environment variables, environment variables override this file, and this file overrides defaults. |
| `.xhtang-harness/state.sqlite3` | Default local state database under the current worktree. |
| `.skills/<skill-name>/SKILL.md` | Default local skill file path. |

Default state and skill paths are worktree-local. Use explicit `--state-path`,
`XHTANG_HARNESS_STATE_PATH`, `--skills-path`, or `XHTANG_HARNESS_SKILLS_PATH`
when you intentionally want a shared path.

Example local config:

```toml
thinking = "enabled"
reasoning_effort = "high"
state_path = ".xhtang-harness/state.sqlite3"
skill_learning = "off"
skills_path = ".skills"
model = "deepseek-v4-pro"
```

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `uv` is not found | Install `uv`, then run `uv sync` from the repository root. |
| Missing API key | Set `DEEPSEEK_API_KEY` before running DeepSeek-backed prompts. |
| Python version error | Run `uv sync` from the repository root so uv can use the project Python version. |
| Empty prompt error | Pass a non-empty prompt. |
| Command is not found | Run it through uv: `uv run xhtang-harness`. |
| `--no-stream` still prints an answer line | Treat `--no-stream` as a stream preference, not a complete quiet mode. |
| JSON output is empty or invalid | Include the word `json` in the prompt, provide a concrete schema or example, and keep the requested output small enough to fit. |
| Skill was not used | Make sure the prompt includes the skill `name` or exact `description`, and that the skill file has valid frontmatter plus a non-empty body. |
| Skill learning did not write files | Use `--skill-learning auto`; `suggest` only emits a proposal. Existing skill directories are not overwritten. |
| State appears missing in another worktree | Default state is worktree-local. Pass the same explicit state path only when shared history is intended. |
