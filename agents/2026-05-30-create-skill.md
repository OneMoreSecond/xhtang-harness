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
- Current source has a DeepSeek provider foundation, while `app.py`, `agent_loop.py`, `config.py`, and `storage/sqlite.py` are still skeletons. This feature should be planned after those MVP slices have usable interfaces. [source: `src/xhtang_harness/providers/deepseek.py`, `src/xhtang_harness/app.py`, `src/xhtang_harness/agent_loop.py`, `src/xhtang_harness/config.py`, `src/xhtang_harness/storage/sqlite.py`]

## Constraint and Assumption

- This task is a planning task only; it does not implement the feature. [source: user request]
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
- Add a small `xhtang_harness.skills` package instead of placing this logic inside the DeepSeek provider, tool executor, or CLI renderer. [source: `doc/module-responsibilities.md`, design decision]
- Add three skill-learning modes: `off`, `suggest`, and `auto`. `off` skips the feature, `suggest` emits and persists a proposal without writing skill files, and `auto` writes validated skill files when the model returns `should_create: true`. [source: original task brief, design decision]
- Keep `off` as the initial default so users do not get unexpected generated files; document `auto` as the mode that satisfies the requested behavior. [source: design decision]
- Use a structured JSON response contract for the reflection call and validate it before any file write. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]
- In the first implementation, allow automatic writing of `SKILL.md`, optional `agents/openai.yaml`, and optional markdown references only. Defer executable scripts and binary assets to manual review. [source: `.codex/skills/.system/skill-creator/SKILL.md`, design decision]
- Never overwrite an existing skill folder by default. On name collision, emit a conflict event and skip writing unless a later explicit overwrite option is added. [source: design decision]
- Write skill files atomically through a temporary directory under `.xhtang-harness/tmp/<run-id>/skill/` and then rename into `.skills/<skill-name>/`. [source: `agents/2026-05-30-mvp-implementation.md`, design decision]
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

### Proposed Module Shape

| Module | Responsibility | Source |
| --- | --- | --- |
| `xhtang_harness.skills.models` | Dataclasses for `SkillLearningMode`, `SkillProposal`, `SkillFile`, and `SkillWriteResult`. | [source: design decision] |
| `xhtang_harness.skills.context` | Build the redacted task summary used by the reflection prompt. | [source: `doc/persistent-data-storage.md`, design decision] |
| `xhtang_harness.skills.reflector` | Create the JSON prompt, call the provider, parse the model response, and return a proposal or skip reason. | [source: original task brief, `.agents/skills/deepseek-api/SKILL.md`] |
| `xhtang_harness.skills.validator` | Enforce skill-name, frontmatter, allowed file paths, content-size, and no-secret checks. | [source: `.codex/skills/.system/skill-creator/SKILL.md`, `doc/external-interfaces.md`] |
| `xhtang_harness.skills.writer` | Write validated skill files atomically under `.skills/` and report conflicts or write failures. | [source: original task brief, design decision] |
| `xhtang_harness.app` | Invoke the post-run hook after a successful run when skill learning is enabled. | [source: `doc/module-responsibilities.md`, design decision] |
| `xhtang_harness.config` | Load skill-learning mode and skill path from command args, environment variables, disk config, and defaults. | [source: `doc/external-interfaces.md`, design decision] |
| `xhtang_harness.events` | Add skill-learning lifecycle events for CLI rendering and persistence. | [source: `doc/runtime-flow-and-reliability.md`, design decision] |

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
| `skill_learning_skipped` | `run_id`, `reason` | [source: design decision] |
| `skill_proposed` | `run_id`, `skill_name`, `reason`, `mode` | [source: design decision] |
| `skill_write_started` | `run_id`, `skill_name`, `target_path` | [source: design decision] |
| `skill_written` | `run_id`, `skill_name`, `target_path`, `file_count` | [source: design decision] |
| `skill_write_failed` | `run_id`, `skill_name`, `error_class`, `message` | [source: design decision] |

### Parallel Worktree Behavior

The default `.skills/` path should be resolved from the current worktree so simultaneous development runs do not write to the same hidden directory by accident. Sharing one skill output directory across worktrees should require an explicit `--skills-path` or `XHTANG_HARNESS_SKILLS_PATH`. [source: `agents/2026-05-30-mvp-implementation.md`, original task brief, design decision]

## Todo

The checkboxes below are implementation tasks for the create-skill feature, not completed by this planning task. [source: user request]

### Phase 0: MVP Dependency Gate

- [ ] Finish or stabilize the MVP app service, agent loop, config loader, storage gateway, and event interfaces that this feature depends on. [source: `agents/2026-05-30-mvp-implementation.md`]
- [ ] Confirm the provider adapter can make a second JSON-output call without tools and without recursively invoking skill learning. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]

### Phase 1: Interfaces And Config

- [ ] Add `--skill-learning off|suggest|auto` and `--skills-path <path>` to the CLI parser. [source: design decision]
- [ ] Add `XHTANG_HARNESS_SKILL_LEARNING` and `XHTANG_HARNESS_SKILLS_PATH` to config loading. [source: `doc/external-interfaces.md`, design decision]
- [ ] Add optional `.xhtang-harness/config.toml` keys for `skill_learning` and `skills_path`. [source: `doc/external-interfaces.md`, design decision]
- [ ] Validate mode values and reject empty or unsafe skill output paths before starting a run. [source: `doc/runtime-flow-and-reliability.md`, design decision]

### Phase 2: Skill Domain And Prompting

- [ ] Add `xhtang_harness.skills.models` with typed proposal and write-result models. [source: design decision]
- [ ] Add `xhtang_harness.skills.context` to build a redacted run summary for reflection. [source: `doc/persistent-data-storage.md`, design decision]
- [ ] Add `xhtang_harness.skills.reflector` with a JSON-output prompt and parser. [source: original task brief, `.agents/skills/deepseek-api/SKILL.md`]
- [ ] Add tests for skip decisions, create decisions, malformed JSON, empty JSON content, and proposal redaction. [source: `.agents/skills/deepseek-api/SKILL.md`, `AGENTS.md`]

### Phase 3: Validation And Writing

- [ ] Add `xhtang_harness.skills.validator` for name, frontmatter, allowed paths, and secret-pattern checks. [source: `.codex/skills/.system/skill-creator/SKILL.md`, design decision]
- [ ] Add `xhtang_harness.skills.writer` to write through a temporary directory and atomically rename into `.skills/<skill-name>/`. [source: original task brief, design decision]
- [ ] Add conflict handling that skips existing skill folders by default. [source: design decision]
- [ ] Add tests for successful write, existing-skill conflict, path traversal rejection, invalid frontmatter, and temporary-directory cleanup. [source: `AGENTS.md`, design decision]

### Phase 4: App, Events, And Storage Integration

- [ ] Invoke skill learning from `xhtang_harness.app` after a successful `run_completed` state. [source: `doc/module-responsibilities.md`, design decision]
- [ ] Skip skill learning for failed, cancelled, and skill-reflection internal runs. [source: `doc/runtime-flow-and-reliability.md`, design decision]
- [ ] Add skill-learning lifecycle events to `xhtang_harness.events`. [source: `doc/runtime-flow-and-reliability.md`, design decision]
- [ ] Persist proposal and write-result payloads as events. [source: `doc/persistent-data-storage.md`, design decision]
- [ ] Render compact CLI messages for skipped, proposed, written, and failed skill-learning outcomes. [source: `doc/ux-expectations.md`, design decision]

### Phase 5: Acceptance And Documentation

- [ ] Update `USAGE.md` with skill-learning modes, `.skills/` output, and troubleshooting. [source: `USAGE.md`, design decision]
- [ ] Update `doc/external-interfaces.md` with the new command arguments, environment variables, disk config keys, and output files. [source: `doc/external-interfaces.md`]
- [ ] Add or update MVP implementation documentation to place this feature after the core MVP loop. [source: `agents/2026-05-30-mvp-implementation.md`]
- [ ] Run `uv run pytest`. [source: `AGENTS.md`]
- [ ] Run `uv run ruff check .`. [source: `AGENTS.md`]
- [ ] Run `uv run ruff format --check .`. [source: `AGENTS.md`]
- [ ] Run `uv run mypy src`. [source: `AGENTS.md`]
- [ ] Manually test `--skill-learning suggest` with a fake or recorded provider response and verify no `.skills/` files are written. [source: design decision]
- [ ] Manually test `--skill-learning auto` and verify `.skills/<skill-name>/SKILL.md` is created only after validation passes. [source: original task brief, design decision]

## Results

Created this implementation plan for the create-skill feature at `agents/2026-05-30-create-skill.md`. No runtime code was changed by this planning task. [source: user request, task work]

Validation results: `uv run pytest` passed with 44 tests, `uv run ruff check .` passed, and `uv run mypy src` passed. `uv run ruff format --check .` failed because tracked baseline file `examples/fib30.py` would be reformatted; this planning task did not touch that file. Local validation caches were removed after the run. [source: command output]
