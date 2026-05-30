from __future__ import annotations

from collections.abc import Iterator

from xhtang_harness.agent_loop import AgentLoop
from xhtang_harness.config import HarnessConfig, require_api_key
from xhtang_harness.events import HarnessEvent
from xhtang_harness.providers.deepseek import (
    DeepSeekConfigurationError,
    DeepSeekProvider,
)
from xhtang_harness.storage.sqlite import SQLiteStore
from xhtang_harness.tools.builtin import default_registry_tools
from xhtang_harness.tools.executor import ToolExecutor
from xhtang_harness.tools.registry import ToolRegistry


def run_harness(config: HarnessConfig) -> Iterator[HarnessEvent]:
    try:
        provider = DeepSeekProvider(
            api_key=require_api_key(config),
            base_url=config.base_url,
        )
    except DeepSeekConfigurationError as error:
        from xhtang_harness.errors import ConfigError

        raise ConfigError(str(error)) from error

    registry = ToolRegistry(default_registry_tools())
    executor = ToolExecutor(registry)
    with SQLiteStore(config.state_path) as store:
        loop = AgentLoop(
            store=store,
            provider=provider,
            registry=registry,
            executor=executor,
        )
        yield from loop.run(config=config)
