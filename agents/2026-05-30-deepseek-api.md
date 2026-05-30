Task ID: 2026-05-30-deepseek-api

# Research on DeepSeek API calling

## Background

This project would use DeepSeek as main LLM provider.

## Goal

read pages with https://api-docs.deepseek.com/zh-cn/ as root.

summarize how to call DeepSeek API in agent harness scenario to a new skill deepseek-api, including both reasoning and non-reasoning mode.

## Scope

Focus on latest DeepSeek v4 Pro model.

---

## Research

| Term | Meaning | Source |
| --- | --- | --- |
| `deepseek-v4-pro` | Current DeepSeek V4 Pro chat model ID for OpenAI-compatible and Anthropic-compatible calls. | [DeepSeek docs: first API call](https://api-docs.deepseek.com/zh-cn/) |
| Thinking mode | DeepSeek mode that returns `reasoning_content` before final `content`; default is enabled. | [DeepSeek docs: thinking mode](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode) |
| Non-thinking mode | Same model with `thinking.type = "disabled"` for lower-latency non-reasoning calls. | [DeepSeek docs: chat completion API](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion) |
| Tool calls | Function-call style external tool requests using `tools`, `tool_choice`, and `tool` response messages. | [DeepSeek docs: Tool Calls](https://api-docs.deepseek.com/zh-cn/guides/tool_calls) |
| Context cache | Default server-side cache that may reduce input-token cost when request prefixes match. | [DeepSeek docs: context disk cache](https://api-docs.deepseek.com/zh-cn/guides/kv_cache) |

- DeepSeek API is compatible with OpenAI and Anthropic API shapes; OpenAI base URL is `https://api.deepseek.com`, Anthropic base URL is `https://api.deepseek.com/anthropic`. [source: DeepSeek docs first API call, Anthropic API]
- Official docs list `deepseek-v4-pro` and `deepseek-v4-flash`; `deepseek-chat` and `deepseek-reasoner` are compatibility aliases scheduled for deprecation on 2026-07-24. [source: DeepSeek docs first API call, update log 2026-04-24]
- Model detail page lists both V4 models with 1M context length, 384K maximum output length, JSON Output support, Tool Calls support, and both thinking and non-thinking modes. [source: DeepSeek docs model and pricing]
- Thinking mode defaults to enabled; OpenAI-compatible calls set `thinking` through SDK `extra_body`, and `reasoning_effort` accepts `high` or `max`. [source: DeepSeek docs thinking mode]
- Thinking mode ignores `temperature`, `top_p`, `presence_penalty`, and `frequency_penalty`; setting them does not fail but does not take effect. [source: DeepSeek docs thinking mode]
- In thinking mode, `reasoning_content` is returned separately from final `content`. When tool calls happen, agent harnesses must preserve assistant messages with `reasoning_content` and `tool_calls` in later requests or the API can return HTTP 400. [source: DeepSeek docs thinking mode]
- `/chat/completions` is stateless, so the harness must send the full conversation history on each turn. [source: DeepSeek docs multi-round chat]
- `user_id` can be used for content safety, KV-cache isolation, and scheduling isolation; in OpenAI SDK calls it should be passed via `extra_body`. [source: DeepSeek docs rate limit and chat completion API]
- JSON Output uses `response_format={"type": "json_object"}`, requires a prompt mentioning JSON and an example schema, and can return empty content in some cases. [source: DeepSeek docs JSON Output]
- API errors relevant to harness retry/reporting include 400 format error, 401 auth failure, 402 insufficient balance, 422 parameter error, 429 rate limit, 500 server fault, and 503 busy. [source: DeepSeek docs error codes]

## Constraint and Assumption

- Preserve the original task text above the separator. [source: root `AGENTS.md`]
- Create the new skill under repo-local `.agents/skills/deepseek-api/` because this repository already stores custom skills under `.agents/skills/`. [source: local filesystem]
- Use only official DeepSeek documentation from `https://api-docs.deepseek.com/zh-cn/` for API behavior. [source: user task]
- Treat `deepseek-v4-pro` as the requested current focus because official docs and update log confirm V4 Pro support as of 2026-04-24. [source: DeepSeek update log]
- The deliverable is a skill, not production DeepSeek client code in `src/`. [source: user task goal]

## Challenges

- DeepSeek API behavior is time-sensitive; model names and compatibility aliases have dated deprecation information. [source: DeepSeek first API call docs]
- Reasoning tool-call loops have a non-obvious state requirement: preserve `reasoning_content` after tool calls. [source: DeepSeek thinking mode docs]
- The skill must be concise enough for future agents to use quickly while still recording critical API edge cases. [source: `skill-creator` skill]

## Decisions

- Create `deepseek-api` as a repo-local skill using `skill-creator` initialization and validation scripts. [source: `skill-creator` skill, local `.agents/skills`]
- Keep the skill self-contained in `SKILL.md` plus generated `agents/openai.yaml`; do not add scripts or long reference files because the calling pattern is mostly procedural guidance. [source: task scope]
- Include both OpenAI-compatible and Anthropic-compatible base URLs, but emphasize OpenAI Chat Completions because it is the documented common path and fits the Python harness. [source: DeepSeek first API call docs]
- Include reasoning and non-reasoning request patterns for `deepseek-v4-pro`. [source: user task scope]
- Include agent-harness-specific guidance for stateless message history, tool calls, `reasoning_content`, JSON mode, `user_id`, cache telemetry, and retryable errors. [source: DeepSeek docs]

## Design

- Initialize `.agents/skills/deepseek-api/`.
- Replace generated skill content with a concise DeepSeek API calling guide.
- Validate the skill folder with the `skill-creator` validation script.
- Run Markdown/content sanity checks and repository tests that do not require missing tools.

## Todo

- [x] Read task document and root instructions.
- [x] Research official DeepSeek API docs.
- [x] Decide target skill location and scope.
- [x] Create `deepseek-api` skill files.
- [x] Validate generated skill metadata.
- [x] Run repository checks.
- [x] Update results and task history.

## Results

- Created `.agents/skills/deepseek-api/SKILL.md` with a DeepSeek V4 Pro agent-harness API guide covering OpenAI-compatible calls, Anthropic-compatible calls, reasoning mode, non-reasoning mode, tool calls, streaming, JSON Output, context-cache telemetry, `user_id`, rate limits, finish reasons, and error handling. [source: `.agents/skills/deepseek-api/SKILL.md`]
- Created `.agents/skills/deepseek-api/agents/openai.yaml` with UI metadata for the new skill. [source: `skill-creator` initializer output]
- Verified the skill with `python3.12 /home/xhtang-sandbox2/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/deepseek-api`. [source: shell validation]
- Verified repository tests with `PYTHONDONTWRITEBYTECODE=1 python3.12 -m pytest -p no:cacheprovider`; 4 tests passed. [source: shell validation]
- Verified Ruff lint and format checks with `python3.12 -m ruff check --no-cache .` and `python3.12 -m ruff format --check --no-cache .`. [source: shell validation]
- `python3.12 -m mypy src` was attempted but could not run because `mypy` is not installed in the current `python3.12` environment. [source: shell validation]
