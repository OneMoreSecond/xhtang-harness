Task ID: 2026-05-30-create-skill

# Remind the agent to create skill after task finished

## Background

I want to improve the self-evolvement ability of agent.

## Target feature

When the goal given by user finishes, send another prompt asking the agent whether this task deserves to create a new skill. If yes, write the new skill files to .skills/.

## Task

plan for this feature based on the MVP plan.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Self-evolvement | The harness can notice repeated or reusable task knowledge and save it as a skill for later agent runs. | [source: original task brief] |
| Skill reflection | A post-run model step that decides whether the completed task deserves a reusable skill. | [source: original task brief, design decision] |
| Skill materialization | Writing validated skill files under `.skills/` after the reflection step returns a positive decision. | [source: original task brief, design decision] |
| Target MVP | The planned local agent harness with prompt input, DeepSeek provider calls, streaming events, optional tools, SQLite persistence, and clear errors. | [source: `doc/mvp.md`] |
| Post-run hook | Application-layer logic that runs after the main user goal reaches a durable terminal state. | [source: `agents/2026-05-30-mvp-implementation.md`, design decision] |
| Skill folder | A folder named after the skill that contains a required `SKILL.md` and optional `agents/`, `references/`, `scripts/`, or `assets/` resources. | [source: `.codex/skills/.system/skill-creator/SKILL.md`] |

- The MVP app service is planned to coordinate CLI requests, storage, provider, tools, and the agent loop. This is the right boundary for a post-run feature because it can observe terminal run status without polluting provider or tool code. [source: `agents/2026-05-30-mvp-implementation.md`, `doc/module-responsibilities.md`]
- The MVP event stream already includes lifecycle events such as `run_started`, `run_completed`, `run_failed`, and `run_cancelled`; skill reflection can add similar events without changing the basic CLI rendering model. [source: `agents/2026-05-30-mvp-implementation.md`, `doc/runtime-flow-and-reliability.md`]
- The planned storage layer persists sessions, runs, messages, tool calls, provider usage, and optional events in SQLite. Skill reflection can initially persist proposal data as events instead of adding a dedicated table. [source: `doc/persistent-data-storage.md`, `agents/2026-05-30-mvp-implementation.md`]
- External-interface precedent already exists for command arguments, environment variables, disk config, local output files, and worktree-local defaults. Skill learning should follow the same precedence and path rules. [source: `doc/external-interfaces.md`]
- DeepSeek guidance supports JSON output and recommends clear JSON instructions, a concrete schema, enough max tokens, and handling empty or malformed JSON responses. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Skill creation guidance requires a `SKILL.md` with YAML frontmatter containing only `name` and `description`, concise imperative body instructions, lowercase hyphen skill names, and validation of generated skills. [source: `.codex/skills/.system/skill-creator/SKILL.md`]
- Current source has the MVP app, agent loop, config, SQLite storage, DeepSeek provider, and built-in `bash` tool needed to implement the first skill-learning slice. [source: `src/xhtang_harness/app.py`, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/config.py`, `src/xhtang_harness/storage/sqlite.py`, `src/xhtang_harness/providers/deepseek.py`, `src/xhtang_harness/tools/builtin.py`]
- Latest acceptance requires two concrete behaviors: stdout must show the agent is thinking about whether to create a skill, and manually created `.skills/<skill-name>/SKILL.md` content must be available when the prompt includes that skill description. [source: latest user instruction]

## Constraint and Assumption

- This task is now an implementation task for a narrow MVP skill-learning slice; the original brief requested planning, but the latest user instruction supplied concrete acceptance criteria. [source: original task brief, latest user instruction]
- The original content above the separator is preserved as the task brief. [source: `AGENTS.md`, original task brief]
- The phrase "send another prompt asking the agent" means an internal post-run LLM call, not a second interactive question to the human user. [source: original task brief, design assumption]
- The requested output location `.skills/` means a repository-local `.skills/` directory under the current working tree unless the user explicitly configures another path. [source: original task brief, design assumption]
- The feature should run after the main user goal has completed successfully; failed and cancelled runs should not create skills in the first version. [source: `doc/runtime-flow-and-reliability.md`, design decision]
- The feature should never store API keys or private credential values in skill files, proposal events, logs, or prompts. [source: `doc/external-interfaces.md`, `doc/persistent-data-storage.md`]
- Tests for this feature must use fake provider responses and temporary directories; they must not require a real DeepSeek key or write to the user's real `.skills/`. [source: `AGENTS.md`, `agents/2026-05-30-mvp-implementation.md`]
- Automatic skill creation is powerful enough to dirty the working tree, so the first implementation should be explicitly enabled through config or CLI rather than silently active in every run. [source: design decision]

## Challenges

- The model needs enough task context to identify reusable learning, but skill files should not leak private user data, secrets, or one-off task details. [source: original task brief, `doc/persistent-data-storage.md`, design decision]
- The second provider call adds latency, cost, and failure modes after the main answer is already complete. [source: `doc/runtime-flow-and-reliability.md`, `.agents/skills/deepseek-api/SKILL.md`]
- Generated skills can be low quality, too broad, too narrow, or duplicative. The feature needs validation and skip criteria. [source: `.codex/skills/.system/skill-creator/SKILL.md`, design decision]
- Writing files from model output creates path traversal and overwrite risks unless file paths, names, and allowed resource types are constrained. [source: design decision]
- A skill-reflection run must not recursively trigger another skill-reflection run. [source: design decision]
- Parallel worktree runs can each create `.skills/` content; shared skill paths need the same explicit opt-in and conflict handling used for shared state paths. [source: `agents/2026-05-30-mvp-implementation.md`, design decision]

## Decisions

- Implement this as an optional post-MVP slice after the main MVP app, agent loop, config, storage, and event interfaces exist. [source: `agents/2026-05-30-mvp-implementation.md`, design decision]
- Add a small `xhtang_harness.skills` module instead of placing this logic inside the DeepSeek provider, tool executor, or CLI renderer. [source: `doc/module-responsibilities.md`, implementation]
- Add three skill-learning modes: `off`, `suggest`, and `auto`. `off` skips the feature, `suggest` emits and persists a proposal without writing skill files, and `auto` writes validated skill files when the model returns `should_create: true`. [source: original task brief, design decision]
- Keep `off` as the initial default so users do not get unexpected generated files; document `auto` as the mode that satisfies the requested behavior. [source: design decision]
- Use a structured JSON response contract for the reflection call and validate it before any file write. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]
- In the first implementation, allow automatic writing of `SKILL.md` and optional markdown references only. Defer `agents/openai.yaml`, executable scripts, and binary assets to a later reviewed slice. [source: `.codex/skills/.system/skill-creator/SKILL.md`, implementation]
- Never overwrite an existing skill folder by default. On name collision, emit `skill_learning_failed` and skip writing unless a later explicit overwrite option is added. [source: implementation]
- Write skill files through a temporary directory under `.xhtang-harness/tmp/skills/` and then rename into `.skills/<skill-name>/`. [source: `src/xhtang_harness/skills.py`]
- Load matching local skills before provider calls by adding a non-persisted system message when the user prompt includes a local skill name or exact description. [source: latest user instruction, `src/xhtang_harness/skills.py`, `src/xhtang_harness/agent_loop.py`]
- Store skill-reflection lifecycle and proposal data as events for the first version instead of adding a dedicated `skill_reflections` table. [source: `doc/persistent-data-storage.md`, design decision]

## Design

### User Flow

| Step | Behavior | Source |
| --- | --- | --- |
| 1 | User runs the normal MVP command with skill learning enabled, such as `uv run xhtang-harness --skill-learning auto "..."`. | [source: original task brief, `doc/external-interfaces.md`, design decision] |
| 2 | The main agent loop handles the user's goal and reaches `run_completed`. | [source: `doc/mvp.md`, `doc/runtime-flow-and-reliability.md`] |
| 3 | The app service builds a redacted skill-reflection context from the run summary, final answer summary, tool names, failure-free outcome, and durable run metadata. | [source: `doc/persistent-data-storage.md`, design decision] |
| 4 | The skill reflector sends a JSON-output prompt to the provider asking whether the completed task deserves a reusable skill. | [source: original task brief, `.agents/skills/deepseek-api/SKILL.md`] |
| 5 | If the response says `should_create: false`, the app emits `skill_learning_skipped` and finishes. | [source: design decision] |
| 6 | If the response says `should_create: true`, the writer validates name, paths, frontmatter, and content limits. | [source: `.codex/skills/.system/skill-creator/SKILL.md`, design decision] |
| 7 | In `suggest` mode, the proposal is persisted and shown without file writes. In `auto` mode, validated files are written under `.skills/<skill-name>/`. | [source: original task brief, design decision] |

### Implemented Module Shape

| Module | Responsibility | Source |
| --- | --- | --- |
| `xhtang_harness.skills` | Dataclasses, local skill matching, reflection prompt/options, JSON parsing, validation, and skill writing for the MVP slice. | [source: `src/xhtang_harness/skills.py`] |
| `xhtang_harness.agent_loop` | Loads matching skill context before provider calls and runs the post-run reflection hook after successful completion. | [source: `src/xhtang_harness/agent_loop.py`] |
| `xhtang_harness.config` | Loads skill-learning mode and skill path from command args, environment variables, disk config, and defaults. | [source: `src/xhtang_harness/config.py`] |
| `xhtang_harness.cli` | Parses skill flags and renders compact skill-learning stdout events. | [source: `src/xhtang_harness/cli.py`] |
| `xhtang_harness.events` | Includes skill-context and skill-learning event types for CLI rendering and persistence. | [source: `src/xhtang_harness/events.py`, `src/xhtang_harness/storage/sqlite.py`] |

### External Interfaces

| User state | Interface | Required | Behavior | Source |
| --- | --- | --- | --- | --- |
| Skill learning mode | `--skill-learning off|suggest|auto` | No | Controls whether the post-run reflection is skipped, proposed only, or allowed to write files. | [source: design decision] |
| Skill output path | `--skills-path <path>` | No | Overrides the default `.skills/` output directory. | [source: original task brief, design decision] |
| Default skill learning mode | `XHTANG_HARNESS_SKILL_LEARNING` | No | Environment fallback for the mode. | [source: `doc/external-interfaces.md`, design decision] |
| Default skill output path | `XHTANG_HARNESS_SKILLS_PATH` | No | Environment fallback for the output directory. | [source: `doc/external-interfaces.md`, design decision] |
| Disk config | `.xhtang-harness/config.toml` keys `skill_learning` and `skills_path` | No | Disk fallback after command args and environment variables. | [source: `doc/external-interfaces.md`, design decision] |
| Generated skill files | `.skills/<skill-name>/...` | Only in `auto` mode with a positive proposal | Stores generated skill files for review and later use. | [source: original task brief, design decision] |

Configuration precedence should remain command argument, then environment variable, then disk config, then code default. [source: `doc/external-interfaces.md`]

### Reflection JSON Contract

The reflector should ask for a JSON object with this shape and reject malformed responses before writing files. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]

```json
{
  "should_create": true,
  "reason": "The task produced reusable workflow knowledge.",
  "skill_name": "short-hyphen-name",
  "description": "What the skill does and when Codex should use it.",
  "skill_body": "Markdown instructions for SKILL.md after the frontmatter.",
  "references": [
    {
      "path": "references/example.md",
      "content": "Optional markdown reference content."
    }
  ]
}
```

Validation rules: [source: `.codex/skills/.system/skill-creator/SKILL.md`, design decision]

- `skill_name` must match lowercase letters, digits, and hyphens and stay under 64 characters. [source: `.codex/skills/.system/skill-creator/SKILL.md`]
- `description` must explain what the skill does and when it should trigger. [source: `.codex/skills/.system/skill-creator/SKILL.md`]
- Generated `SKILL.md` frontmatter must contain only `name` and `description`. [source: `.codex/skills/.system/skill-creator/SKILL.md`]
- Allowed automatic file paths are `SKILL.md`, `agents/openai.yaml`, and `references/*.md`. [source: design decision]
- Paths containing `..`, absolute paths, symlinks, or files outside the target skill folder must be rejected. [source: design decision]
- Content should be redacted for secrets and should avoid copying raw user transcripts into the skill. [source: `doc/persistent-data-storage.md`, design decision]

### Event Additions

| Event | Payload minimum | Source |
| --- | --- | --- |
| `skill_learning_started` | `run_id`, `mode`, `skills_path` | [source: design decision] |
| `skill_context_loaded` | `run_id`, `skills_path`, `skill_count` | [source: latest user instruction, implementation] |
| `skill_learning_skipped` | `run_id`, `reason` | [source: design decision] |
| `skill_proposed` | `run_id`, `skill_name`, `reason`, `mode` | [source: design decision] |
| `skill_write_started` | `run_id`, `skill_name`, `target_path` | [source: design decision] |
| `skill_written` | `run_id`, `skill_name`, `target_path`, `file_count` | [source: design decision] |
| `skill_learning_failed` | `run_id`, `error_class`, `message` | [source: implementation] |

### Parallel Worktree Behavior

The default `.skills/` path should be resolved from the current worktree so simultaneous development runs do not write to the same hidden directory by accident. Sharing one skill output directory across worktrees should require an explicit `--skills-path` or `XHTANG_HARNESS_SKILLS_PATH`. [source: `agents/2026-05-30-mvp-implementation.md`, original task brief, design decision]

## Todo

The checkboxes below track the implemented MVP slice and remaining follow-up work. [source: latest user instruction]

### Phase 0: MVP Dependency Gate

- [x] Finish or stabilize the MVP app service, agent loop, config loader, storage gateway, and event interfaces that this feature depends on. [source: `src/xhtang_harness/app.py`, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/config.py`, `src/xhtang_harness/storage/sqlite.py`]
- [x] Confirm the provider adapter can make a second JSON-output call without tools and without recursively invoking skill learning. [source: `src/xhtang_harness/agent_loop.py`, focused tests]

### Phase 1: Interfaces And Config

- [x] Add `--skill-learning off|suggest|auto` and `--skills-path <path>` to the CLI parser. [source: `src/xhtang_harness/cli.py`]
- [x] Add `XHTANG_HARNESS_SKILL_LEARNING` and `XHTANG_HARNESS_SKILLS_PATH` to config loading. [source: `src/xhtang_harness/config.py`]
- [x] Add optional `.xhtang-harness/config.toml` keys for `skill_learning` and `skills_path`. [source: `src/xhtang_harness/config.py`]
- [x] Validate mode values before starting a run. [source: `src/xhtang_harness/config.py`, `tests/test_config.py`]

### Phase 2: Skill Domain And Prompting

- [x] Add typed proposal and write-result models in `xhtang_harness.skills`. [source: `src/xhtang_harness/skills.py`]
- [x] Add a bounded run summary for reflection. [source: `src/xhtang_harness/skills.py`]
- [x] Add JSON-output reflection prompt/options and parser. [source: `src/xhtang_harness/skills.py`]
- [ ] Add tests for skip decisions, create decisions, malformed JSON, empty JSON content, and proposal redaction. [source: `.agents/skills/deepseek-api/SKILL.md`, `AGENTS.md`]

### Phase 3: Validation And Writing

- [x] Add validation for skill name and allowed reference paths. [source: `src/xhtang_harness/skills.py`]
- [x] Add writer to write through a temporary directory and rename into `.skills/<skill-name>/`. [source: `src/xhtang_harness/skills.py`]
- [x] Add conflict handling that skips existing skill folders by default. [source: `src/xhtang_harness/skills.py`]
- [ ] Add tests for successful write, existing-skill conflict, path traversal rejection, invalid frontmatter, and temporary-directory cleanup. [source: `AGENTS.md`, design decision]

### Phase 4: App, Events, And Storage Integration

- [x] Invoke skill learning after a successful `run_completed` state. [source: `src/xhtang_harness/agent_loop.py`]
- [x] Skip skill learning for failed, cancelled, and skill-reflection internal runs. [source: `src/xhtang_harness/agent_loop.py`]
- [x] Add skill-learning lifecycle events to `xhtang_harness.events`. [source: `src/xhtang_harness/events.py`]
- [x] Persist proposal and write-result payloads as events. [source: `src/xhtang_harness/storage/sqlite.py`, `src/xhtang_harness/agent_loop.py`]
- [x] Render compact CLI messages for skipped, proposed, written, and failed skill-learning outcomes. [source: `src/xhtang_harness/cli.py`]

### Phase 5: Acceptance And Documentation

- [x] Update `USAGE.md` with skill-learning modes, `.skills/` output, and troubleshooting. [source: `USAGE.md`]
- [x] Update `doc/external-interfaces.md` with the new command arguments, environment variables, disk config keys, and output files. [source: `doc/external-interfaces.md`]
- [ ] Add or update MVP implementation documentation to place this feature after the core MVP loop. [source: `agents/2026-05-30-mvp-implementation.md`]
- [x] Run `uv run pytest`. [source: command output]
- [x] Run `uv run ruff check .`. [source: command output]
- [ ] Run `uv run ruff format --check .`. [source: command output]
- [x] Run `uv run mypy src`. [source: command output]
- [x] Manually test `--skill-learning suggest` with a real provider response and verify no `.skills/` files are written by suggest mode. [source: live acceptance command output]
- [x] Test `--skill-learning auto` and verify `.skills/<skill-name>/SKILL.md` is created only after validation passes. [source: `tests/test_agent_loop.py`]

## Results

Implemented the MVP create-skill slice. The harness now loads matching local `.skills/<skill-name>/SKILL.md` bodies into provider context when the prompt contains the skill name or exact description, supports `--skill-learning off|suggest|auto`, asks a JSON reflection prompt after successful runs when enabled, renders `skill_learning_started: thinking whether to create a skill` on stdout, and writes validated `SKILL.md` files in `auto` mode. [source: latest user instruction, `src/xhtang_harness/skills.py`, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/cli.py`]

Usage example: `uv run xhtang-harness --skill-learning suggest "Use when the prompt mentions the cerulean abacus checklist. What secret is hidden in the matching local skill?"`. The live acceptance run used a manually created `.skills/cerulean-abacus/SKILL.md` with description `Use when the prompt mentions the cerulean abacus checklist.` and body secret `hidden-secret: lava-mint-7319`; stdout included `skill_context_loaded: 1 local skill(s)`, an answer containing `lava-mint-7319`, and `skill_learning_started: thinking whether to create a skill`. [source: live acceptance command output]

Validation results: `uv run pytest` passed with 50 tests, `uv run ruff check .` passed, and `uv run mypy src` passed. `uv run ruff format --check .` still fails only because existing tracked baseline file `examples/fib30.py` would be reformatted; this implementation did not touch that unrelated file. [source: command output]
