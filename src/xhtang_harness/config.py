from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from xhtang_harness.errors import ConfigError
from xhtang_harness.providers.deepseek import (
    DEFAULT_DEEPSEEK_BASE_URL,
    DEFAULT_DEEPSEEK_MODEL,
)

ThinkingMode = Literal["enabled", "disabled"]
ReasoningEffort = Literal["high", "max"]

_VALID_THINKING = {"enabled", "disabled"}
_VALID_REASONING = {"high", "max"}


@dataclass(frozen=True)
class HarnessConfig:
    prompt: str
    session: str | None
    thinking: ThinkingMode
    reasoning_effort: ReasoningEffort | None
    stream: bool
    json_output: bool
    state_path: Path
    debug: bool
    api_key: str | None
    base_url: str
    model: str
    user_id: str | None


@dataclass(frozen=True)
class ConfigOverrides:
    session: str | None = None
    thinking: str | None = None
    reasoning_effort: str | None = None
    stream: bool | None = None
    json_output: bool = False
    state_path: Path | None = None
    debug: bool = False


def load_config(
    *,
    prompt: str,
    overrides: ConfigOverrides | None = None,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> HarnessConfig:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        raise ConfigError("prompt must not be empty")

    active_overrides = overrides if overrides is not None else ConfigOverrides()
    active_env = env if env is not None else os.environ
    active_cwd = cwd if cwd is not None else Path.cwd()
    disk_config = _read_disk_config(active_cwd)

    thinking = _validate_thinking(
        _first_str(
            active_overrides.thinking,
            active_env.get("XHTANG_HARNESS_THINKING"),
            _str_from_config(disk_config, "thinking"),
            "enabled",
        )
    )
    reasoning_effort = _optional_reasoning(
        _first_str(
            active_overrides.reasoning_effort,
            active_env.get("XHTANG_HARNESS_REASONING_EFFORT"),
            _str_from_config(disk_config, "reasoning_effort"),
            "high",
        )
    )
    state_path = _resolve_state_path(
        override=active_overrides.state_path,
        env_value=active_env.get("XHTANG_HARNESS_STATE_PATH"),
        disk_config=disk_config,
        cwd=active_cwd,
    )

    return HarnessConfig(
        prompt=clean_prompt,
        session=active_overrides.session,
        thinking=thinking,
        reasoning_effort=reasoning_effort if thinking == "enabled" else None,
        stream=True if active_overrides.stream is None else active_overrides.stream,
        json_output=active_overrides.json_output,
        state_path=state_path,
        debug=active_overrides.debug,
        api_key=_optional_first_str(active_env.get("DEEPSEEK_API_KEY")),
        base_url=_first_str(
            active_env.get("DEEPSEEK_BASE_URL"),
            _str_from_config(disk_config, "base_url"),
            DEFAULT_DEEPSEEK_BASE_URL,
        ),
        model=_first_str(
            active_env.get("DEEPSEEK_MODEL"),
            _str_from_config(disk_config, "model"),
            DEFAULT_DEEPSEEK_MODEL,
        ),
        user_id=_optional_first_str(
            active_env.get("XHTANG_HARNESS_USER_ID"),
            _str_from_config(disk_config, "user_id"),
        ),
    )


def require_api_key(config: HarnessConfig) -> str:
    if config.api_key is None or not config.api_key.strip():
        raise ConfigError("DEEPSEEK_API_KEY is required for provider calls")
    return config.api_key


def _read_disk_config(cwd: Path) -> Mapping[str, object]:
    config_path = cwd / ".xhtang-harness" / "config.toml"
    if not config_path.exists():
        return {}
    try:
        with config_path.open("rb") as config_file:
            value = tomllib.load(config_file)
    except OSError as error:
        raise ConfigError(f"could not read config file: {config_path}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML config file: {config_path}") from error
    return value


def _resolve_state_path(
    *,
    override: Path | None,
    env_value: str | None,
    disk_config: Mapping[str, object],
    cwd: Path,
) -> Path:
    if override is not None:
        return override.expanduser()
    if env_value is not None and env_value.strip():
        return Path(env_value).expanduser()
    disk_state = _str_from_config(disk_config, "state_path")
    if disk_state is not None:
        return Path(disk_state).expanduser()
    return cwd / ".xhtang-harness" / "state.sqlite3"


def _str_from_config(config: Mapping[str, object], key: str) -> str | None:
    value = config.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"config field {key} must be a string")
    return value


def _first_str(*values: str | None) -> str:
    for value in values:
        if value is not None and value.strip():
            return value
    raise ConfigError("missing required configuration value")


def _optional_first_str(*values: str | None) -> str | None:
    for value in values:
        if value is not None and value.strip():
            return value
    return None


def _validate_thinking(value: str) -> ThinkingMode:
    if value not in _VALID_THINKING:
        raise ConfigError("thinking must be enabled or disabled")
    return cast(ThinkingMode, value)


def _optional_reasoning(value: str | None) -> ReasoningEffort | None:
    if value is None:
        return None
    if value not in _VALID_REASONING:
        raise ConfigError("reasoning effort must be high or max")
    return cast(ReasoningEffort, value)
