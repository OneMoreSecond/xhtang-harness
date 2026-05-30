from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from xhtang_harness.providers.deepseek import (
    DeepSeekConfigurationError,
    DeepSeekMessage,
    DeepSeekOptions,
    DeepSeekProvider,
    DeepSeekProviderError,
    DeepSeekToolCall,
)


@dataclass
class FakeCompletions:
    response: object
    calls: list[dict[str, object]] = field(default_factory=list)

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if isinstance(self.response, BaseException):
            raise self.response
        return self.response


@dataclass
class FakeChat:
    completions: FakeCompletions


@dataclass
class FakeClient:
    chat: FakeChat


class FakeHTTPError(RuntimeError):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"provider failed with HTTP {status_code}")
        self.status_code = status_code


def make_fake_client(response: object) -> tuple[FakeClient, FakeCompletions]:
    completions = FakeCompletions(response)
    return FakeClient(FakeChat(completions)), completions


def make_response() -> object:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Done",
                    reasoning_content="private reasoning state",
                    tool_calls=[
                        SimpleNamespace(
                            id="call_1",
                            type="function",
                            function=SimpleNamespace(
                                name="lookup",
                                arguments='{"query": "weather"}',
                            ),
                        )
                    ],
                ),
                finish_reason="tool_calls",
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            prompt_cache_hit_tokens=6,
            prompt_cache_miss_tokens=4,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=2),
        ),
    )


def test_complete_builds_explicit_deepseek_payload() -> None:
    client, completions = make_fake_client(make_response())
    provider = DeepSeekProvider(client=client)

    response = provider.complete(
        [
            DeepSeekMessage(role="system", content="Answer as JSON."),
            DeepSeekMessage(role="user", content="Check the weather."),
        ],
        DeepSeekOptions(
            reasoning_effort="max",
            user_id="test-user",
            max_tokens=128,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "lookup",
                        "description": "Look up external information.",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        ),
    )

    assert completions.calls == [
        {
            "model": "deepseek-v4-pro",
            "messages": [
                {"role": "system", "content": "Answer as JSON."},
                {"role": "user", "content": "Check the weather."},
            ],
            "extra_body": {
                "thinking": {"type": "enabled"},
                "user_id": "test-user",
            },
            "reasoning_effort": "max",
            "max_tokens": 128,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup",
                        "description": "Look up external information.",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        }
    ]
    assert response.content == "Done"
    assert response.reasoning_content == "private reasoning state"
    assert response.finish_reason == "tool_calls"
    assert response.tool_calls == (
        DeepSeekToolCall(
            id="call_1",
            name="lookup",
            arguments='{"query": "weather"}',
        ),
    )
    assert response.usage is not None
    assert response.usage.prompt_tokens == 10
    assert response.usage.completion_tokens == 5
    assert response.usage.total_tokens == 15
    assert response.usage.reasoning_tokens == 2
    assert response.usage.prompt_cache_hit_tokens == 6
    assert response.usage.prompt_cache_miss_tokens == 4


def test_complete_preserves_reasoning_tool_call_history() -> None:
    client, completions = make_fake_client(make_response())
    provider = DeepSeekProvider(client=client)

    provider.complete(
        [
            DeepSeekMessage(
                role="assistant",
                content=None,
                reasoning_content="needed for continuation",
                tool_calls=(
                    DeepSeekToolCall(
                        id="call_1",
                        name="lookup",
                        arguments='{"query": "weather"}',
                    ),
                ),
            ),
            DeepSeekMessage(
                role="tool",
                content="sunny",
                tool_call_id="call_1",
            ),
        ]
    )

    assert completions.calls[0]["messages"] == [
        {
            "role": "assistant",
            "content": None,
            "reasoning_content": "needed for continuation",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "lookup",
                        "arguments": '{"query": "weather"}',
                    },
                }
            ],
        },
        {
            "role": "tool",
            "content": "sunny",
            "tool_call_id": "call_1",
        },
    ]


def test_complete_sends_non_thinking_json_options() -> None:
    client, completions = make_fake_client(make_response())
    provider = DeepSeekProvider(client=client)

    provider.complete(
        [DeepSeekMessage(role="user", content="Return json.")],
        DeepSeekOptions(
            thinking="disabled",
            temperature=0.2,
            response_format={"type": "json_object"},
        ),
    )

    assert completions.calls[0]["extra_body"] == {"thinking": {"type": "disabled"}}
    assert completions.calls[0]["temperature"] == 0.2
    assert completions.calls[0]["response_format"] == {"type": "json_object"}
    assert "reasoning_effort" not in completions.calls[0]


def test_complete_requires_messages() -> None:
    client, _ = make_fake_client(make_response())
    provider = DeepSeekProvider(client=client)

    with pytest.raises(ValueError, match="messages must contain at least one message"):
        provider.complete([])


def test_complete_classifies_retryable_provider_error() -> None:
    client, _ = make_fake_client(FakeHTTPError(429))
    provider = DeepSeekProvider(client=client)

    with pytest.raises(DeepSeekProviderError) as error:
        provider.complete([DeepSeekMessage(role="user", content="hello")])

    assert error.value.status_code == 429
    assert error.value.retryable is True
    assert str(error.value) == "DeepSeek provider request failed with HTTP 429"


def test_provider_requires_api_key_without_injected_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(DeepSeekConfigurationError, match="DEEPSEEK_API_KEY"):
        DeepSeekProvider()
