Task ID: 2026-05-30-multiple-round-input

# Support multiple round input

## Background

currently the user can only give prompt via '--goal' argument.

## Goal

before cli exits, ask user for additional prompt input.

## Hints

The skill learning, if enabled, should be done for every input roun.

## Verification the feature

After finishing the old Fibonacci usage example, ask the agent to modify the .py file and also calculate the cumsum of Finbonacci numbers.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Prompt | The user request passed into `load_config(prompt=...)` and stored as a user message for a run. | [source: `src/xhtang_harness/cli.py`, `src/xhtang_harness/agent_loop.py`] |
| Session | The persisted conversation container returned in the `run_started` event payload as `session_id`. | [source: `src/xhtang_harness/agent_loop.py`] |
| Run | One execution of the agent loop for one prompt inside a session. | [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/storage/sqlite.py`] |
| Skill learning | Optional reflection/write step triggered after an agent run completes. | [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/skills.py`] |

- `main()` currently parses one positional prompt, loads one `HarnessConfig`, streams one `run_harness(config)` event sequence, then exits. [source: `src/xhtang_harness/cli.py`]
- `run_harness()` creates one `AgentLoop` and delegates to `loop.run(config=config)`. [source: `src/xhtang_harness/app.py`]
- `AgentLoop.run()` uses `config.session` to continue or create a session, emits `run_started` with the resolved session id, records `config.prompt` as a user message, and then runs provider/tool turns. [source: `src/xhtang_harness/agent_loop.py`]
- When no tool calls remain, `AgentLoop._run_turns()` marks the run completed, emits `run_completed`, and invokes `_run_skill_learning()` for that run. [source: `src/xhtang_harness/agent_loop.py`]
- Existing CLI tests monkeypatch `xhtang_harness.cli.run_harness`, so the multi-round CLI behavior can be tested without provider calls. [source: `tests/test_cli.py`]

## Constraint and Assumption

- Keep the change in the CLI layer so provider, storage, tool execution, and skill learning behavior stay unchanged. [source: design decision, `src/xhtang_harness/cli.py`, `src/xhtang_harness/agent_loop.py`]
- Additional prompts should continue the same session created by the first run, otherwise the follow-up instruction would lose conversation history. [source: user goal, `src/xhtang_harness/agent_loop.py`]
- Only interactive terminals should be prompted for another input; non-interactive stdin should preserve current one-shot behavior and avoid hanging tests/scripts. [source: design decision]
- Blank additional input should end the CLI cleanly. [source: design decision]
- If a run is cancelled or failed, the CLI should keep the existing exit-code behavior and not ask for another prompt. [source: `src/xhtang_harness/cli.py`]
- Skill learning should happen once for every completed prompt round before asking for the next prompt. [source: user hint, `src/xhtang_harness/agent_loop.py`]

## Challenges

- `run_completed` may not be the last event when skill learning is enabled, so the CLI must track whether a run completed instead of only checking the final event type. [source: `src/xhtang_harness/agent_loop.py`]
- The first run can create a new session when `--session` is omitted; the CLI must capture the emitted session id for follow-up rounds. [source: `src/xhtang_harness/agent_loop.py`]
- Prompt text must not be written to stdout in JSON mode because stdout is used for JSON event lines. [source: `src/xhtang_harness/cli.py`]

## Decisions

- Implement a small interactive loop in `main()` that runs the current config, captures `session_id` from `run_started`, then reads one additional prompt from stdin after a completed round. [source: design decision]
- Reuse the existing `HarnessConfig` with `dataclasses.replace()` for follow-up rounds, changing only `prompt` and `session`. [source: design decision, `src/xhtang_harness/config.py`]
- Print the additional-prompt question to stderr, so stdout remains reserved for harness events and JSON lines. [source: design decision]
- Skip additional prompting when `sys.stdin.isatty()` is false. [source: design decision]
- Add CLI tests that prove a second prompt is accepted after post-completion skill-learning events and that non-interactive stdin remains one-shot. [source: `tests/test_cli.py`]

## Design

The CLI keeps one-shot behavior for scripts and tests, but in an interactive terminal it repeats completed runs:

1. Load the first config from the CLI prompt and overrides. [source: `src/xhtang_harness/cli.py`]
2. Run `run_harness(config)` and render events exactly as today. [source: `src/xhtang_harness/cli.py`]
3. Record the resolved `session_id` from the `run_started` event. [source: `src/xhtang_harness/agent_loop.py`]
4. Let all events finish, including skill-learning events. [source: user hint, `src/xhtang_harness/agent_loop.py`]
5. If the run completed and stdin is interactive, ask for an additional prompt on stderr. [source: design decision]
6. If the user enters non-blank text, run another round with the same session id. [source: design decision]

## Todo

- [x] Read the task brief, CLI, app entry point, agent loop, config, skill learning, and CLI tests. [source: task work]
- [x] Create the required task-plan structure and history file. [source: `AGENTS.md`]
- [x] Implement the CLI multi-round input loop. [source: design decision]
- [x] Add focused CLI tests. [source: `tests/test_cli.py`]
- [x] Add a two-round skill-secret verification for session continuity. [source: user instruction, `agents/2026-05-30-create-skill.md`, `tests/test_agent_loop.py`]
- [x] Run targeted and project checks. [source: `AGENTS.md`]
- [x] Review edited markdown and record final results. [source: `AGENTS.md`]

## Results

Implemented multi-round CLI input in `main()`. After a completed run, the CLI now asks for `additional prompt (blank to exit):` on stderr when stdin is interactive. Non-blank input starts another run with the same resolved session id, so follow-up prompts keep conversation history. Blank input, EOF, or non-interactive stdin exits cleanly. [source: `src/xhtang_harness/cli.py`]

Skill learning remains owned by `AgentLoop`; because the CLI waits for the full `run_harness(config)` event stream before asking for the next prompt, skill learning still runs once per completed input round. [source: `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`]

Added CLI tests for accepting a second prompt after post-completion skill-learning events, reusing the session id for the follow-up run, and preserving one-shot behavior when stdin is not interactive. [source: `tests/test_cli.py`]

Added the requested session-continuity verification based on the local skill format from `agents/2026-05-30-create-skill.md`: a temporary skill contains secret `hidden-secret: saffron-vector-8842`; round one prompts the agent to read the matching skill; round two asks for the previous secret without matching the skill text. The test asserts the second provider request contains the prior assistant message with the secret and does not reload skill context, proving the answer can come from continued session history. [source: user instruction, `agents/2026-05-30-create-skill.md`, `tests/test_agent_loop.py`]

Validation passed: `uv run pytest tests/test_cli.py`, `uv run pytest tests/test_agent_loop.py tests/test_cli.py`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check src/xhtang_harness/cli.py tests/test_cli.py tests/test_agent_loop.py`, and `uv run mypy src`. Repo-wide `uv run ruff format --check .` still reports `examples/fib30.py` would be reformatted; that file was not modified for this task and has no worktree diff. [source: command output]
