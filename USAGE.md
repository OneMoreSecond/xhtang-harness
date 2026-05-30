# Usage

Use `xhtang-harness` from this repository or worktree.

## Requirements

- `uv`
- Python 3.12
- `DEEPSEEK_API_KEY` for real provider calls

## Setup

Create or refresh the local environment:

```bash
uv sync
```

Set the DeepSeek API key:

```bash
export DEEPSEEK_API_KEY="..."
```

## MVP Goal

Ask the harness to create a Python file that calculates the first 30 Fibonacci
numbers:

```bash
uv run xhtang-harness \
  "Create fibonacci_first_30.py in the current directory. Use the bash tool to write the file. The script should calculate and print the first 30 Fibonacci numbers."
```

The harness exposes a `bash` tool, so the model can write the file with a shell
command when the user explicitly asks for a local file change.

After the run, inspect the generated file:

```bash
uv run python fibonacci_first_30.py
```

## Local Skills

The harness reads local skills from `.skills/<skill-name>/SKILL.md`. A skill
matches when the prompt includes its `name` or `description`; the skill body is
then sent to the provider as a system instruction for that run.

Example skill:

```markdown
---
name: example-skill
description: Use when the prompt mentions example-skill.
---

Follow these reusable instructions.
```

Enable post-run skill reflection when you want the harness to ask whether the
completed task deserves a reusable skill:

```bash
uv run xhtang-harness --skill-learning suggest "Summarize this workflow."
uv run xhtang-harness --skill-learning auto "Summarize this workflow."
```

`suggest` prints and persists the proposal without writing files. `auto` writes
validated skills under `.skills/` when the model returns `should_create: true`.

## Built-In Tools

| Tool | Purpose |
| --- | --- |
| `get_current_time` | Returns the current UTC time. |
| `bash` | Runs `/bin/bash -lc` with captured exit code, stdout, stderr, optional `cwd`, and a bounded timeout. |

## Options

| Option | Description |
| --- | --- |
| `goal` | Prompt describing what you want the harness to do. |
| `--session <id>` | Continue or create a specific local session. |
| `--thinking enabled\|disabled` | Select DeepSeek thinking mode. |
| `--reasoning-effort high\|max` | Select reasoning effort when thinking is enabled. |
| `--stream` / `--no-stream` | Render run events as they are produced. |
| `--json` | Request JSON provider output and render event lines as JSON. |
| `--state-path <path>` | Override the SQLite state database path. |
| `--skill-learning off\|suggest\|auto` | Control post-run skill reflection. Defaults to `off`. |
| `--skills-path <path>` | Override the local skill directory. Defaults to `.skills`. |
| `--debug` | Print local runtime details such as the effective state path. |
| `--version` | Print the package version and exit. |

By default, state is stored under the current worktree at
`.xhtang-harness/state.sqlite3`.

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `uv` is not found | Install `uv`, then run `uv sync` again from the repository root. |
| Missing API key | Set `DEEPSEEK_API_KEY` before running provider-backed prompts. |
| Python version error | Run `uv sync` from the repository root so uv can use the project Python version. |
| Empty prompt error | Pass a non-empty prompt. |
| Command is not found | Run it through uv: `uv run xhtang-harness`. |
| Skill was not used | Make sure the prompt includes the skill `name` or exact `description`. |
