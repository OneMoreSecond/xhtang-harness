from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, cast

DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-pro"

DeepSeekRole = Literal["system", "user", "assistant", "tool"]
ThinkingMode = Literal["enabled", "disabled"]
ReasoningEffort = Literal["high", "max"]

_MISSING = object()
_VALID_ROLES = {"system", "user", "assistant", "tool"}
_VALID_THINKING_MODES = {"enabled", "disabled"}
_VALID_REASONING_EFFORTS = {"high", "max"}
_RETRYABLE_STATUS_CODES = {429, 500, 503}


class _ChatCompletions(Protocol):
    def create(self, **kwargs: object) -> object: ...


class _ChatClient(Protocol):
    completions: _ChatCompletions


class _DeepSeekClient(Protocol):
    chat: _ChatClient


class DeepSeekConfigurationError(RuntimeError):
    """Raised when the provider cannot be configured for real API calls."""


class DeepSeekProviderError(RuntimeError):
    """Normalized provider failure with retry guidance for the agent loop."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None,
        retryable: bool,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


@dataclass(frozen=True)
class DeepSeekToolCall:
    id: str
    name: str
    arguments: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("tool call id must not be empty")
        if not self.name.strip():
            raise ValueError("tool call name must not be empty")


@dataclass(frozen=True)
class DeepSeekMessage:
    role: DeepSeekRole
    content: str | None
    reasoning_content: str | None = None
    tool_calls: tuple[DeepSeekToolCall, ...] = ()
    tool_call_id: str | None = None

    def __post_init__(self) -> None:
        if self.role not in _VALID_ROLES:
            raise ValueError(f"unsupported message role: {self.role}")
        if self.role != "assistant" and self.content is None:
            raise ValueError(f"{self.role} messages require content")
        if self.role != "assistant" and self.reasoning_content is not None:
            raise ValueError("reasoning_content is only valid for assistant messages")
        if self.role != "assistant" and self.tool_calls:
            raise ValueError("tool_calls are only valid for assistant messages")
        if self.role == "tool" and not self.tool_call_id:
            raise ValueError("tool messages require tool_call_id")
        if self.role != "tool" and self.tool_call_id is not None:
            raise ValueError("tool_call_id is only valid for tool messages")


@dataclass(frozen=True)
class DeepSeekOptions:
    model: str = DEFAULT_DEEPSEEK_MODEL
    thinking: ThinkingMode = "enabled"
    reasoning_effort: ReasoningEffort | None = "high"
    temperature: float | None = None
    max_tokens: int | None = None
    user_id: str | None = None
    tools: Sequence[Mapping[str, object]] | None = None
    tool_choice: object | None = None
    response_format: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.thinking not in _VALID_THINKING_MODES:
            raise ValueError(f"unsupported thinking mode: {self.thinking}")
        if (
            self.reasoning_effort is not None
            and self.reasoning_effort not in _VALID_REASONING_EFFORTS
        ):
            raise ValueError(f"unsupported reasoning effort: {self.reasoning_effort}")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("max_tokens must be positive when provided")
        if self.user_id is not None and not self.user_id.strip():
            raise ValueError("user_id must not be empty when provided")


@dataclass(frozen=True)
class DeepSeekUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens: int | None = None
    prompt_cache_hit_tokens: int | None = None
    prompt_cache_miss_tokens: int | None = None


@dataclass(frozen=True)
class DeepSeekResponse:
    content: str
    reasoning_content: str | None
    tool_calls: tuple[DeepSeekToolCall, ...]
    finish_reason: str | None
    usage: DeepSeekUsage | None


class DeepSeekProvider:
    def __init__(
        self,
        *,
        client: _DeepSeekClient | None = None,
        api_key: str | None = None,
        base_url: str = DEFAULT_DEEPSEEK_BASE_URL,
    ) -> None:
        if client is None:
            self._client = _build_openai_client(api_key=api_key, base_url=base_url)
        else:
            self._client = client

    def complete(
        self,
        messages: Sequence[DeepSeekMessage],
        options: DeepSeekOptions | None = None,
    ) -> DeepSeekResponse:
        if not messages:
            raise ValueError("messages must contain at least one message")

        request_options = options if options is not None else DeepSeekOptions()
        request = _build_request(messages, request_options)

        try:
            response = self._client.chat.completions.create(**request)
        except DeepSeekProviderError:
            raise
        except Exception as error:
            raise _provider_error_from(error) from error

        return _response_from_chat_completion(response)


def _build_openai_client(
    *,
    api_key: str | None,
    base_url: str,
) -> _DeepSeekClient:
    resolved_api_key = (
        api_key if api_key is not None else os.environ.get("DEEPSEEK_API_KEY")
    )
    if resolved_api_key is None or not resolved_api_key.strip():
        raise DeepSeekConfigurationError(
            "DEEPSEEK_API_KEY is required when no client is injected"
        )
    if not base_url.strip():
        raise DeepSeekConfigurationError("base_url must not be empty")

    try:
        from openai import OpenAI
    except ImportError as error:
        raise DeepSeekConfigurationError(
            "the openai package is required when no client is injected"
        ) from error

    return cast(
        _DeepSeekClient,
        OpenAI(api_key=resolved_api_key, base_url=base_url),
    )


def _build_request(
    messages: Sequence[DeepSeekMessage],
    options: DeepSeekOptions,
) -> dict[str, object]:
    extra_body: dict[str, object] = {"thinking": {"type": options.thinking}}
    if options.user_id is not None:
        extra_body["user_id"] = options.user_id

    request: dict[str, object] = {
        "model": options.model,
        "messages": [_message_to_payload(message) for message in messages],
        "extra_body": extra_body,
    }

    if options.thinking == "enabled" and options.reasoning_effort is not None:
        request["reasoning_effort"] = options.reasoning_effort
    if options.max_tokens is not None:
        request["max_tokens"] = options.max_tokens
    if options.temperature is not None:
        request["temperature"] = options.temperature
    if options.tools is not None:
        request["tools"] = list(options.tools)
    if options.tool_choice is not None:
        request["tool_choice"] = options.tool_choice
    if options.response_format is not None:
        request["response_format"] = dict(options.response_format)

    return request


def _message_to_payload(message: DeepSeekMessage) -> dict[str, object]:
    payload: dict[str, object] = {
        "role": message.role,
        "content": message.content,
    }

    if message.reasoning_content is not None:
        payload["reasoning_content"] = message.reasoning_content
    if message.tool_calls:
        payload["tool_calls"] = [
            _tool_call_to_payload(tool_call) for tool_call in message.tool_calls
        ]
    if message.tool_call_id is not None:
        payload["tool_call_id"] = message.tool_call_id

    return payload


def _tool_call_to_payload(tool_call: DeepSeekToolCall) -> dict[str, object]:
    return {
        "id": tool_call.id,
        "type": "function",
        "function": {
            "name": tool_call.name,
            "arguments": tool_call.arguments,
        },
    }


def _response_from_chat_completion(response: object) -> DeepSeekResponse:
    choices = _field(response, "choices")
    if (
        not isinstance(choices, Sequence)
        or isinstance(choices, str | bytes)
        or len(choices) == 0
    ):
        raise DeepSeekProviderError(
            "DeepSeek provider response did not include choices",
            status_code=None,
            retryable=False,
        )

    first_choice = choices[0]
    message = _field(first_choice, "message")
    finish_reason = _optional_str(
        _field(first_choice, "finish_reason", None),
        "finish_reason",
    )

    if finish_reason == "insufficient_system_resource":
        raise DeepSeekProviderError(
            "DeepSeek provider reported insufficient system resources",
            status_code=None,
            retryable=True,
        )

    return DeepSeekResponse(
        content=_content_from_message(message),
        reasoning_content=_optional_str(
            _field(message, "reasoning_content", None),
            "reasoning_content",
        ),
        tool_calls=_tool_calls_from_message(message),
        finish_reason=finish_reason,
        usage=_usage_from(_field(response, "usage", None)),
    )


def _content_from_message(message: object) -> str:
    content = _field(message, "content", None)
    if content is None:
        return ""
    return _required_str(content, "content")


def _tool_calls_from_message(message: object) -> tuple[DeepSeekToolCall, ...]:
    raw_tool_calls = _field(message, "tool_calls", None)
    if raw_tool_calls is None:
        return ()
    if not isinstance(raw_tool_calls, Sequence) or isinstance(
        raw_tool_calls,
        str | bytes,
    ):
        raise DeepSeekProviderError(
            "DeepSeek provider response included invalid tool_calls",
            status_code=None,
            retryable=False,
        )

    return tuple(
        _tool_call_from_response(raw_tool_call) for raw_tool_call in raw_tool_calls
    )


def _tool_call_from_response(raw_tool_call: object) -> DeepSeekToolCall:
    function = _field(raw_tool_call, "function")
    return DeepSeekToolCall(
        id=_required_str(_field(raw_tool_call, "id"), "tool call id"),
        name=_required_str(_field(function, "name"), "tool call function name"),
        arguments=_required_str(
            _field(function, "arguments"),
            "tool call function arguments",
        ),
    )


def _usage_from(usage: object) -> DeepSeekUsage | None:
    if usage is None:
        return None

    completion_details = _field(usage, "completion_tokens_details", None)
    reasoning_tokens = None
    if completion_details is not None:
        reasoning_tokens = _optional_int(
            _field(completion_details, "reasoning_tokens", None),
            "reasoning_tokens",
        )

    return DeepSeekUsage(
        prompt_tokens=_optional_int(
            _field(usage, "prompt_tokens", None),
            "prompt_tokens",
        ),
        completion_tokens=_optional_int(
            _field(usage, "completion_tokens", None),
            "completion_tokens",
        ),
        total_tokens=_optional_int(_field(usage, "total_tokens", None), "total_tokens"),
        reasoning_tokens=reasoning_tokens,
        prompt_cache_hit_tokens=_optional_int(
            _field(usage, "prompt_cache_hit_tokens", None),
            "prompt_cache_hit_tokens",
        ),
        prompt_cache_miss_tokens=_optional_int(
            _field(usage, "prompt_cache_miss_tokens", None),
            "prompt_cache_miss_tokens",
        ),
    )


def _field(value: object, name: str, default: object = _MISSING) -> object:
    if isinstance(value, Mapping) and name in value:
        return value[name]
    if hasattr(value, name):
        return getattr(value, name)
    if default is not _MISSING:
        return default
    raise DeepSeekProviderError(
        f"DeepSeek provider response missing {name}",
        status_code=None,
        retryable=False,
    )


def _required_str(value: object, field_name: str) -> str:
    if isinstance(value, str):
        return value
    raise DeepSeekProviderError(
        f"DeepSeek provider response included invalid {field_name}",
        status_code=None,
        retryable=False,
    )


def _optional_str(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_str(value, field_name)


def _optional_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise DeepSeekProviderError(
        f"DeepSeek provider response included invalid {field_name}",
        status_code=None,
        retryable=False,
    )


def _provider_error_from(error: Exception) -> DeepSeekProviderError:
    status_code = _status_code_from_error(error)
    retryable = status_code in _RETRYABLE_STATUS_CODES
    if status_code is None:
        return DeepSeekProviderError(
            "DeepSeek provider request failed",
            status_code=None,
            retryable=False,
        )
    return DeepSeekProviderError(
        f"DeepSeek provider request failed with HTTP {status_code}",
        status_code=status_code,
        retryable=retryable,
    )


def _status_code_from_error(error: Exception) -> int | None:
    direct_status_code = getattr(error, "status_code", None)
    if isinstance(direct_status_code, int) and not isinstance(direct_status_code, bool):
        return direct_status_code

    response = getattr(error, "response", None)
    response_status_code = getattr(response, "status_code", None)
    if isinstance(response_status_code, int) and not isinstance(
        response_status_code,
        bool,
    ):
        return response_status_code

    if isinstance(response, Mapping):
        mapped_status_code = response.get("status_code")
        if isinstance(mapped_status_code, int) and not isinstance(
            mapped_status_code,
            bool,
        ):
            return mapped_status_code

    return None
