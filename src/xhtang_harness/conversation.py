from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

MessageRole = Literal["system", "user", "assistant", "tool"]
RunStatus = Literal["running", "completed", "failed", "cancelled"]
SessionStatus = Literal["active", "archived"]


def new_id(prefix: str) -> str:
    if not prefix.strip():
        raise ValueError("id prefix must not be empty")
    return f"{prefix}_{uuid4().hex}"


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str | None
    id: str = field(default_factory=lambda: new_id("msg"))
    reasoning_content: str | None = None
    tool_call_id: str | None = None
    tool_calls: tuple[ToolCall, ...] = ()

    def __post_init__(self) -> None:
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
class ProviderUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None
    prompt_cache_hit_tokens: int | None = None
    prompt_cache_miss_tokens: int | None = None


@dataclass(frozen=True)
class Session:
    id: str
    title: str
    status: SessionStatus


@dataclass(frozen=True)
class Run:
    id: str
    session_id: str
    status: RunStatus
