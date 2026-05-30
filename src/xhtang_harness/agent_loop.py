from __future__ import annotations

from collections.abc import Callable, Generator, Iterator
from time import sleep

from xhtang_harness.config import HarnessConfig
from xhtang_harness.conversation import Message, ProviderUsage, ToolCall
from xhtang_harness.errors import HarnessError, ToolRunError
from xhtang_harness.events import HarnessEvent
from xhtang_harness.providers.deepseek import (
    DeepSeekMessage,
    DeepSeekOptions,
    DeepSeekProvider,
    DeepSeekProviderError,
    DeepSeekResponse,
    DeepSeekToolCall,
    DeepSeekUsage,
)
from xhtang_harness.skills import (
    SkillError,
    build_reflection_messages,
    matching_skill_context,
    parse_skill_decision,
    reflection_options,
    write_skill,
)
from xhtang_harness.storage.sqlite import SQLiteStore
from xhtang_harness.tools.executor import ToolExecutor
from xhtang_harness.tools.registry import ToolRegistry

CancelCheck = Callable[[], bool]
Sleep = Callable[[float], None]


class AgentLoop:
    def __init__(
        self,
        *,
        store: SQLiteStore,
        provider: DeepSeekProvider,
        registry: ToolRegistry,
        executor: ToolExecutor,
        max_tool_turns: int = 8,
        max_retries: int = 2,
        sleep_fn: Sleep = sleep,
    ) -> None:
        self._store = store
        self._provider = provider
        self._registry = registry
        self._executor = executor
        self._max_tool_turns = max_tool_turns
        self._max_retries = max_retries
        self._sleep = sleep_fn

    def run(
        self,
        *,
        config: HarnessConfig,
        cancel_requested: CancelCheck | None = None,
    ) -> Iterator[HarnessEvent]:
        is_cancelled = (
            cancel_requested if cancel_requested is not None else _not_cancelled
        )
        session = self._store.get_or_create_session(
            requested_session_id=config.session,
            title=config.prompt[:80],
        )
        run = self._store.start_run(session.id)

        yield from self._emit(
            run.id,
            HarnessEvent(
                "run_started",
                {
                    "run_id": run.id,
                    "session_id": session.id,
                    "state_path": str(config.state_path),
                },
            ),
        )

        user_message = Message(role="user", content=config.prompt)
        self._store.add_message(session.id, run.id, user_message)
        yield from self._emit(
            run.id,
            HarnessEvent(
                "message_recorded",
                {"message_id": user_message.id, "role": user_message.role},
            ),
        )
        skill_context, skill_count = matching_skill_context(
            config.prompt,
            config.skills_path,
        )
        if skill_context is not None:
            yield from self._emit(
                run.id,
                HarnessEvent(
                    "skill_context_loaded",
                    {
                        "run_id": run.id,
                        "skills_path": str(config.skills_path),
                        "skill_count": skill_count,
                    },
                ),
            )

        try:
            yield from self._run_turns(
                config=config,
                session_id=session.id,
                run_id=run.id,
                skill_context=skill_context,
                is_cancelled=is_cancelled,
            )
        except HarnessError as error:
            self._store.fail_run(run.id, error.code, error.message)
            yield from self._emit(
                run.id,
                HarnessEvent(
                    "run_failed",
                    {
                        "run_id": run.id,
                        "error_class": error.code,
                        "message": error.message,
                    },
                ),
            )
        except DeepSeekProviderError as error:
            self._store.fail_run(run.id, "provider_error", str(error))
            yield from self._emit(
                run.id,
                HarnessEvent(
                    "run_failed",
                    {
                        "run_id": run.id,
                        "error_class": "provider_error",
                        "message": str(error),
                        "retryable": error.retryable,
                    },
                ),
            )

    def _run_turns(
        self,
        *,
        config: HarnessConfig,
        session_id: str,
        run_id: str,
        skill_context: str | None,
        is_cancelled: CancelCheck,
    ) -> Iterator[HarnessEvent]:
        for tool_turn in range(self._max_tool_turns + 1):
            if is_cancelled():
                self._store.cancel_run(run_id)
                yield from self._emit(
                    run_id,
                    HarnessEvent("run_cancelled", {"run_id": run_id}),
                )
                return

            response = yield from self._provider_turn(
                config=config,
                session_id=session_id,
                run_id=run_id,
                skill_context=skill_context,
            )
            assistant_message = _assistant_message_from_response(response)
            self._store.add_message(session_id, run_id, assistant_message)
            yield from self._emit(
                run_id,
                HarnessEvent(
                    "message_recorded",
                    {
                        "message_id": assistant_message.id,
                        "role": assistant_message.role,
                    },
                ),
            )

            if response.usage is not None:
                self._store.record_usage(run_id, _usage_from_deepseek(response.usage))

            if response.content:
                yield from self._emit(
                    run_id,
                    HarnessEvent("answer_delta", {"text": response.content}),
                )

            if not response.tool_calls:
                self._store.complete_run(run_id)
                yield from self._emit(
                    run_id,
                    HarnessEvent("run_completed", {"run_id": run_id}),
                )
                yield from self._run_skill_learning(
                    config=config,
                    run_id=run_id,
                    final_answer=response.content,
                )
                return

            if tool_turn == self._max_tool_turns:
                raise ToolRunError(
                    "tool-call loop exceeded the maximum number of turns"
                )

            for provider_tool_call in response.tool_calls:
                yield from self._execute_tool_call(
                    run_id=run_id,
                    session_id=session_id,
                    provider_tool_call=provider_tool_call,
                    is_cancelled=is_cancelled,
                )
                if is_cancelled():
                    return

    def _provider_turn(
        self,
        *,
        config: HarnessConfig,
        session_id: str,
        run_id: str,
        skill_context: str | None,
    ) -> Generator[HarnessEvent, None, DeepSeekResponse]:
        request_event = HarnessEvent(
            "provider_request_started",
            {
                "model": config.model,
                "thinking_mode": config.thinking,
            },
        )
        yield from self._emit(run_id, request_event)

        stored_messages = tuple(
            _deepseek_message_from_message(message)
            for message in self._store.load_messages(session_id)
        )
        if skill_context is None:
            messages = stored_messages
        else:
            messages = (
                DeepSeekMessage(role="system", content=skill_context),
                *stored_messages,
            )
        options = DeepSeekOptions(
            model=config.model,
            thinking=config.thinking,
            reasoning_effort=config.reasoning_effort,
            user_id=config.user_id,
            tools=self._registry.provider_tools(),
            response_format={"type": "json_object"} if config.json_output else None,
        )

        attempt = 0
        while True:
            try:
                response = self._provider.complete(messages, options)
                return response
            except DeepSeekProviderError as error:
                if not error.retryable or attempt >= self._max_retries:
                    raise
                attempt += 1
                delay = float(2 ** (attempt - 1))
                yield from self._emit(
                    run_id,
                    HarnessEvent(
                        "retry_scheduled",
                        {
                            "error_class": "provider_error",
                            "attempt": attempt,
                            "delay_seconds": delay,
                        },
                    ),
                )
                self._sleep(delay)

    def _run_skill_learning(
        self,
        *,
        config: HarnessConfig,
        run_id: str,
        final_answer: str,
    ) -> Iterator[HarnessEvent]:
        if config.skill_learning == "off":
            return

        yield from self._emit(
            run_id,
            HarnessEvent(
                "skill_learning_started",
                {
                    "run_id": run_id,
                    "mode": config.skill_learning,
                    "skills_path": str(config.skills_path),
                },
            ),
        )

        try:
            response = self._provider.complete(
                build_reflection_messages(config=config, final_answer=final_answer),
                reflection_options(config),
            )
            decision = parse_skill_decision(response.content)
            if not decision.should_create:
                yield from self._emit(
                    run_id,
                    HarnessEvent(
                        "skill_learning_skipped",
                        {"run_id": run_id, "reason": decision.reason},
                    ),
                )
                return

            yield from self._emit(
                run_id,
                HarnessEvent(
                    "skill_proposed",
                    {
                        "run_id": run_id,
                        "skill_name": decision.skill_name or "",
                        "reason": decision.reason,
                        "mode": config.skill_learning,
                    },
                ),
            )
            if config.skill_learning == "suggest":
                return

            target_path = config.skills_path / (decision.skill_name or "")
            yield from self._emit(
                run_id,
                HarnessEvent(
                    "skill_write_started",
                    {
                        "run_id": run_id,
                        "skill_name": decision.skill_name or "",
                        "target_path": str(target_path),
                    },
                ),
            )
            write_result = write_skill(decision, config.skills_path)
            yield from self._emit(
                run_id,
                HarnessEvent(
                    "skill_written",
                    {
                        "run_id": run_id,
                        "skill_name": write_result.skill_name,
                        "target_path": str(write_result.target_path),
                        "file_count": write_result.file_count,
                    },
                ),
            )
        except (DeepSeekProviderError, SkillError) as error:
            yield from self._emit(
                run_id,
                HarnessEvent(
                    "skill_learning_failed",
                    {
                        "run_id": run_id,
                        "error_class": type(error).__name__,
                        "message": str(error),
                    },
                ),
            )

    def _execute_tool_call(
        self,
        *,
        run_id: str,
        session_id: str,
        provider_tool_call: DeepSeekToolCall,
        is_cancelled: CancelCheck,
    ) -> Iterator[HarnessEvent]:
        if is_cancelled():
            self._store.cancel_run(run_id)
            yield from self._emit(
                run_id,
                HarnessEvent("run_cancelled", {"run_id": run_id}),
            )
            return

        stored_tool_call = self._store.record_tool_call(
            run_id=run_id,
            provider_tool_call_id=provider_tool_call.id,
            name=provider_tool_call.name,
            arguments_json=provider_tool_call.arguments,
        )
        yield from self._emit(
            run_id,
            HarnessEvent(
                "tool_call_started",
                {
                    "tool_call_id": provider_tool_call.id,
                    "name": provider_tool_call.name,
                },
            ),
        )

        try:
            result = self._executor.execute(
                name=provider_tool_call.name,
                arguments_json=provider_tool_call.arguments,
            )
        except ToolRunError as error:
            self._store.finish_tool_call(
                stored_tool_call_id=stored_tool_call.id,
                status="failed",
                result_text=None,
                error_message=error.message,
            )
            yield from self._emit(
                run_id,
                HarnessEvent(
                    "tool_call_finished",
                    {
                        "tool_call_id": provider_tool_call.id,
                        "status": "failed",
                        "summary": error.message,
                    },
                ),
            )
            raise

        self._store.finish_tool_call(
            stored_tool_call_id=stored_tool_call.id,
            status="completed",
            result_text=result,
            error_message=None,
        )
        self._store.add_message(
            session_id,
            run_id,
            Message(
                role="tool",
                content=result,
                tool_call_id=provider_tool_call.id,
            ),
        )
        yield from self._emit(
            run_id,
            HarnessEvent(
                "tool_call_finished",
                {
                    "tool_call_id": provider_tool_call.id,
                    "status": "completed",
                    "summary": result[:200],
                },
            ),
        )

    def _emit(self, run_id: str, event: HarnessEvent) -> Iterator[HarnessEvent]:
        self._store.record_event(run_id, event)
        yield event


def _assistant_message_from_response(response: DeepSeekResponse) -> Message:
    return Message(
        role="assistant",
        content=response.content,
        reasoning_content=response.reasoning_content,
        tool_calls=tuple(
            ToolCall(
                id=tool_call.id,
                name=tool_call.name,
                arguments=tool_call.arguments,
            )
            for tool_call in response.tool_calls
        ),
    )


def _deepseek_message_from_message(message: Message) -> DeepSeekMessage:
    return DeepSeekMessage(
        role=message.role,
        content=message.content,
        reasoning_content=message.reasoning_content,
        tool_call_id=message.tool_call_id,
        tool_calls=tuple(
            DeepSeekToolCall(
                id=tool_call.id,
                name=tool_call.name,
                arguments=tool_call.arguments,
            )
            for tool_call in message.tool_calls
        ),
    )


def _usage_from_deepseek(usage: DeepSeekUsage) -> ProviderUsage:
    return ProviderUsage(
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        reasoning_tokens=usage.reasoning_tokens,
        prompt_cache_hit_tokens=usage.prompt_cache_hit_tokens,
        prompt_cache_miss_tokens=usage.prompt_cache_miss_tokens,
    )


def _not_cancelled() -> bool:
    return False
