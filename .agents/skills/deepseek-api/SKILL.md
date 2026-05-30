---
name: deepseek-api
description: Build, review, or debug DeepSeek API integrations for agent harnesses using DeepSeek V4 models, especially deepseek-v4-pro. Use when working with OpenAI-compatible or Anthropic-compatible DeepSeek calls, reasoning versus non-reasoning mode, tool calls, JSON output, user_id isolation, context-cache usage, rate limits, migration away from deepseek-chat/deepseek-reasoner aliases, or DeepSeek API error handling.
---

# DeepSeek API

Use this skill to design or review DeepSeek API calls in an agent harness. Facts below come from official DeepSeek API docs checked on 2026-05-30; re-check the docs before changing model names, prices, limits, or deprecation dates. [source: DeepSeek API docs, https://api-docs.deepseek.com/zh-cn/]

## Source Labels

| Label | Source |
| --- | --- |
| First Call | https://api-docs.deepseek.com/zh-cn/ |
| Pricing | https://api-docs.deepseek.com/zh-cn/quick_start/pricing |
| Thinking | https://api-docs.deepseek.com/zh-cn/guides/thinking_mode |
| Multi-Round | https://api-docs.deepseek.com/zh-cn/guides/multi_round_chat |
| Tool Calls | https://api-docs.deepseek.com/zh-cn/guides/tool_calls |
| JSON Output | https://api-docs.deepseek.com/zh-cn/guides/json_mode |
| Cache | https://api-docs.deepseek.com/zh-cn/guides/kv_cache |
| Rate Limit | https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit |
| Errors | https://api-docs.deepseek.com/zh-cn/quick_start/error_codes |
| Chat API | https://api-docs.deepseek.com/zh-cn/api/create-chat-completion |
| Anthropic | https://api-docs.deepseek.com/zh-cn/guides/anthropic_api |
| Agent Integrations | https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code |
| Updates | https://api-docs.deepseek.com/zh-cn/updates |

## Model Choice

- Prefer `deepseek-v4-pro` for high-quality agent work. [source: First Call, Pricing]
- Use OpenAI-compatible calls by default: `base_url="https://api.deepseek.com"`. [source: First Call]
- Use Anthropic-compatible calls only when integrating with Anthropic-shaped clients; its base URL is `https://api.deepseek.com/anthropic`. [source: First Call, Anthropic]
- Avoid new usage of `deepseek-chat` and `deepseek-reasoner`; official docs say both aliases are scheduled for deprecation on 2026-07-24. [source: First Call, Updates]
- Treat `deepseek-v4-pro` and `deepseek-v4-flash` as V4 model IDs; docs list 1M context, 384K max output, JSON Output, Tool Calls, and thinking/non-thinking support for both. [source: Pricing]

## Request Modes

Use the same model ID for both reasoning and non-reasoning; switch with `thinking.type`. [source: Thinking, Chat API]

```python
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
```

Reasoning mode for hard planning, code-agent loops, tool-heavy work, and ambiguous tasks. [source: Thinking]

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    reasoning_effort="high",  # use "max" for complex agent work
    extra_body={
        "thinking": {"type": "enabled"},
        "user_id": user_id,
    },
)
```

Non-reasoning mode for low-latency chat, routing, summarization, extraction, or deterministic tool-free steps. [source: Thinking, Chat API]

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    temperature=0.2,
    extra_body={
        "thinking": {"type": "disabled"},
        "user_id": user_id,
    },
)
```

Notes:

- Thinking mode defaults to enabled. Set `thinking.type` explicitly so harness behavior is clear. [source: Thinking, Chat API]
- `reasoning_effort` accepts `high` and `max`; docs map `low`/`medium` to `high` and `xhigh` to `max` for compatibility. [source: Thinking, Chat API]
- In thinking mode, do not rely on `temperature`, `top_p`, `presence_penalty`, or `frequency_penalty`; docs say those settings do not take effect. [source: Thinking]
- Pass `user_id` through `extra_body` when using the OpenAI SDK; do not include private user data in it. [source: Rate Limit, Chat API]

## Agent Loop

DeepSeek `/chat/completions` is stateless, so send the complete message history on every request. [source: Multi-Round]

Use this loop shape:

1. Build `messages` from persisted conversation state. [source: Multi-Round]
2. Call `chat.completions.create(...)`. [source: Chat API]
3. Append the assistant message to `messages`, preserving `content`, `reasoning_content`, and `tool_calls` when present. [source: Thinking]
4. If `tool_calls` is present, validate `function.arguments` as JSON against the tool schema before executing. [source: Chat API]
5. Append each tool result as `{"role": "tool", "tool_call_id": tool.id, "content": result}`. [source: Tool Calls, Chat API]
6. Repeat until the assistant response has no tool calls. [source: Tool Calls, Thinking]

Reasoning-specific rule:

- If a thinking-mode assistant message includes tool calls, preserve its `reasoning_content` in later requests. Missing reasoning state after tool calls can produce HTTP 400. [source: Thinking]
- If there were no tool calls between user turns, `reasoning_content` is not needed for the next turn, but preserving the full assistant message is the simpler harness policy. [source: Thinking]
- Do not show `reasoning_content` to end users by default; treat it as provider-side reasoning state and log it only under explicit internal-debug controls. [source: Design decision based on Thinking docs and harness safety practice]

## Streaming

Set `stream=True` for incremental output. Collect `delta.reasoning_content` separately from `delta.content` in thinking mode. [source: Thinking, Chat API]

```python
reasoning_text = ""
answer_text = ""

for chunk in stream:
    delta = chunk.choices[0].delta
    if getattr(delta, "reasoning_content", None):
        reasoning_text += delta.reasoning_content
    if getattr(delta, "content", None):
        answer_text += delta.content
```

Use `stream_options={"include_usage": True}` when usage telemetry is needed with streaming. [source: Chat API]

## Structured Output

Use JSON Output for extraction or machine-readable planner responses. [source: JSON Output]

```python
response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=messages,
    response_format={"type": "json_object"},
    max_tokens=2048,
)
```

Requirements:

- Include the word `json` in a system or user message. [source: JSON Output, Chat API]
- Include a concrete JSON example or schema description in the prompt. [source: JSON Output]
- Set enough `max_tokens` so the JSON is not truncated. [source: JSON Output]
- Handle rare empty `content` responses by retrying with a stricter prompt or falling back to normal text mode. [source: JSON Output]

## Cache And Cost Telemetry

DeepSeek context disk cache is on by default and needs no request parameter. [source: Cache]

Harness guidance:

- Keep stable system prompts and long reusable context prefixes byte-for-byte stable to improve cache hits. [source: Cache]
- Track `usage.prompt_cache_hit_tokens` and `usage.prompt_cache_miss_tokens`. [source: Cache, Chat API]
- Do not assume cache hits are guaranteed; docs describe cache behavior as best effort. [source: Cache]

## Limits And Errors

As of the checked docs, account-level concurrency is 500 for `deepseek-v4-pro` and 2500 for `deepseek-v4-flash`. [source: Rate Limit]

Handle errors by class:

- 400: fix malformed request body; also check reasoning tool-call history preservation. [source: Errors, Thinking]
- 401: fix API key configuration. [source: Errors]
- 402: surface billing or balance problem. [source: Errors]
- 422: fix invalid parameters. [source: Errors]
- 429: retry with bounded exponential backoff and reduce concurrency. [source: Errors, Rate Limit]
- 500 or 503: retry with backoff and circuit breaking. [source: Errors]

Watch `finish_reason`: `tool_calls` means continue the tool loop, `length` means raise max output or compress context, `content_filter` means report a filtered response, and `insufficient_system_resource` should be treated as retryable infrastructure pressure. [source: Chat API]

## Anthropic-Compatible Calls

Use this path only when the surrounding library expects Anthropic APIs. [source: Anthropic]

```python
import os

import anthropic

os.environ["ANTHROPIC_BASE_URL"] = "https://api.deepseek.com/anthropic"
os.environ["ANTHROPIC_API_KEY"] = os.environ["DEEPSEEK_API_KEY"]

client = anthropic.Anthropic()

message = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Hello"}],
)
```

For Claude Code-style environments, configure the Anthropic base URL and token to DeepSeek values; prefer `deepseek-v4-pro` for main work and `deepseek-v4-flash` for cheaper subagent/background work. [source: First Call, Anthropic, Agent Integrations]
