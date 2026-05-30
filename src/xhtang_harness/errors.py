from __future__ import annotations


class HarnessError(RuntimeError):
    """Base class for user-facing harness failures."""

    code = "harness_error"
    exit_code = 1

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigError(HarnessError):
    code = "config_error"
    exit_code = 2


class ProviderRunError(HarnessError):
    code = "provider_error"

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class ToolRunError(HarnessError):
    code = "tool_error"


class StorageError(HarnessError):
    code = "storage_error"


class RunCancelled(HarnessError):
    code = "cancelled"
    exit_code = 130
