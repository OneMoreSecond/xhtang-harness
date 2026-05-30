Task ID: 2026-05-30-deepseek-provider

# Implement providers.deepseek module

## Previous works

- doc/module-responsibilities.md
- deepseek-api skill

## Goal


Implement providers.deepseek module wrapping original API.
Expose clean API for agent harness conversation.

## Requirements

Ensure you are working on a git worktree checkout.
Commit and push the feature branch when you finish works.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| Provider adapter | Module that translates harness messages and options into DeepSeek API calls, then normalizes responses. | [source: `doc/module-responsibilities.md`] |
| DeepSeek V4 Pro | Target model ID `deepseek-v4-pro` for agent harness work. | [source: `.agents/skills/deepseek-api/SKILL.md`] |
| Thinking mode | DeepSeek mode controlled by `thinking.type` that can return provider-side `reasoning_content`. | [source: `.agents/skills/deepseek-api/SKILL.md`] |
| Usage metadata | Provider token and cache-hit accounting returned by the API. | [source: `.agents/skills/deepseek-api/SKILL.md`, `doc/persistent-data-storage.md`] |

- Current checkout is a git worktree on branch `worktree/deepseek-provider`. [source: `git worktree list --porcelain`]
- The package now includes `xhtang_harness.providers.deepseek` as the first provider adapter, while the existing CLI demo remains unchanged. [source: `src/xhtang_harness/providers/deepseek.py`, `src/xhtang_harness/cli.py`]
- Runtime dependencies now include `openai>=2.38.0`, with dev tooling still managed by uv. [source: `pyproject.toml`, `uv.lock`]
- The architecture doc assigns `xhtang_harness.providers.deepseek` responsibility for request construction, streaming chunk handling, `reasoning_content` preservation, provider error classification, and usage metadata. [source: `doc/module-responsibilities.md`]
- DeepSeek API guidance recommends OpenAI-compatible calls through `https://api.deepseek.com`, explicit `thinking.type`, `user_id` in `extra_body`, and preserving assistant `reasoning_content` when tool calls occur. [source: `.agents/skills/deepseek-api/SKILL.md`]

## Constraint and Assumption

- Preserve the original task text above the separator. [source: `AGENTS.md`]
- Keep the first implementation narrow: provider request/response normalization and error classification, not the full agent loop, storage layer, or tool executor. [source: task goal, `doc/module-responsibilities.md`]
- Add tests before or alongside implementation. [source: `AGENTS.md`]
- Use uv for checks and lockfile updates if runtime dependencies change. [source: `AGENTS.md`, `README.md`]
- Assume the provider module should be usable with an injected fake client in tests so tests do not require a real DeepSeek API key or network access. [source: design decision]

## Challenges

- Adding the OpenAI SDK gives the shortest real DeepSeek integration path but changes runtime dependencies and requires updating `uv.lock`. [source: `.agents/skills/deepseek-api/SKILL.md`, `pyproject.toml`]
- DeepSeek-specific fields such as `thinking` and `user_id` are not part of the base OpenAI chat message body, so the adapter needs an explicit options surface. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Response objects from SDKs and test fakes may be object-shaped rather than dictionaries, so normalization should handle both without broad magic. [source: design decision]

## Decisions

- Implement `src/xhtang_harness/providers/deepseek.py` and `src/xhtang_harness/providers/__init__.py`. [source: `doc/module-responsibilities.md`]
- Add `openai` as a runtime dependency and lazily create the SDK client only when no client is injected. [source: `.agents/skills/deepseek-api/SKILL.md`, design decision]
- Expose dataclasses for messages, options, tool calls, usage, and responses so the later agent loop can depend on stable harness-owned types. [source: `doc/module-responsibilities.md`]
- Keep this adapter synchronous for the first implementation because the current CLI and tests are synchronous. [source: `src/xhtang_harness/cli.py`, design decision]
- Classify HTTP status failures into retryable/non-retryable provider errors according to the DeepSeek skill. [source: `.agents/skills/deepseek-api/SKILL.md`]

## Design

- Add a provider package with a `DeepSeekProvider` class.
- Accept normalized `DeepSeekMessage` values and `DeepSeekOptions`.
- Convert messages into OpenAI-compatible chat-completion payloads, preserving `reasoning_content` and `tool_calls` when present.
- Send explicit DeepSeek `thinking.type`, optional `user_id`, optional tool schemas, optional JSON response format, and optional token limits.
- Normalize the first returned choice into `DeepSeekResponse` with content, reasoning content, tool calls, finish reason, and usage.
- Convert provider HTTP errors into `DeepSeekProviderError` with `status_code` and `retryable`.

## Todo

- [x] Read task document, AGENTS instructions, previous DeepSeek API skill, and architecture docs.
- [x] Confirm this checkout is a git worktree on the target feature branch.
- [x] Add focused provider tests with an injected fake client.
- [x] Implement `xhtang_harness.providers.deepseek`.
- [x] Add runtime dependency and refresh the uv lockfile if needed.
- [x] Run pytest, Ruff, format check, and mypy through uv.
- [x] Review markdown task files for stale content and update results.
- [x] Commit and push the feature branch.

## Results

- Added `src/xhtang_harness/providers/deepseek.py` with harness-owned dataclasses for messages, options, tool calls, usage, responses, configuration errors, and provider errors. [source: `src/xhtang_harness/providers/deepseek.py`]
- Added `DeepSeekProvider.complete(...)` for synchronous OpenAI-compatible DeepSeek chat completions with explicit `thinking.type`, optional `user_id`, optional reasoning effort, optional tool schemas, optional JSON response format, optional token limit, and optional temperature. [source: `src/xhtang_harness/providers/deepseek.py`, `.agents/skills/deepseek-api/SKILL.md`]
- Preserved assistant `reasoning_content` and `tool_calls` in outgoing continuation messages, and normalized incoming content, reasoning content, tool calls, finish reason, and usage/cache telemetry. [source: `src/xhtang_harness/providers/deepseek.py`, `tests/test_deepseek_provider.py`]
- Added `openai>=2.38.0` and refreshed `uv.lock` through `uv add openai`. [source: `pyproject.toml`, `uv.lock`, shell validation]
- Verified `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src` pass. [source: shell validation]
- Reviewed the task markdown and replaced planning-state findings with implementation-state findings before commit. [source: `agents/2026-05-30-deepseek-provider.md`]
- Committed implementation as `bb08473` and pushed branch `worktree/deepseek-provider` to `origin`. [source: git commit output, git push output]
