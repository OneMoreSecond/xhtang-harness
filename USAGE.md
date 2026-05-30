# Usage

Use `xhtang-harness` from this repository.

## Requirements

- `uv`
- Python 3.12

## Setup

Create or refresh the local environment:

```bash
uv sync
```

## Run

Run the demo with the default goal:

```bash
uv run xhtang-harness
```

Run it with your own goal:

```bash
uv run xhtang-harness "Show a usable agent harness demo"
```

Expected output:

```text
xhtang-harness demo
version: 0.1.0
goal: Show a usable agent harness demo
status: ready
```

Show the installed version:

```bash
uv run xhtang-harness --version
```

## Options

| Option | Description |
| --- | --- |
| `goal` | Optional text describing what you want the harness to run. |
| `--version` | Print the package version and exit. |

If `goal` is omitted, the command uses `Show a usable agent harness demo`.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| `uv` is not found | Install `uv`, then run `uv sync` again from the repository root. |
| Python version error | Run `uv sync` from the repository root so uv can use the project Python version. |
| Empty goal error | Pass a non-empty goal, for example `uv run xhtang-harness "Test goal"`. |
| Command is not found | Run it through uv: `uv run xhtang-harness`. |
| Output only says `status: ready` | That is the expected demo output for this version. |
