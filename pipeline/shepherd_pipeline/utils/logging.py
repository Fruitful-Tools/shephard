"""Unified logging utilities for Prefect + Loguru integration."""

import contextlib
from typing import TYPE_CHECKING, Any

from loguru import logger as loguru_logger
from prefect import get_run_logger
from prefect.exceptions import MissingContextError

if TYPE_CHECKING:
    from logging import Logger, LoggerAdapter


class HybridLogger:
    """Logger that combines Prefect's get_run_logger with Loguru for enhanced logging."""

    def __init__(self) -> None:
        """Initialize hybrid logger."""
        self._prefect_logger: Logger | LoggerAdapter[Logger] | None = None
        self._setup_prefect_logger()

    def _setup_prefect_logger(self) -> None:
        """Setup Prefect logger if in run context."""
        with contextlib.suppress(MissingContextError):
            self._prefect_logger = get_run_logger()

    def _log_to_both(self, level: str, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log to both Prefect and Loguru loggers."""
        # Log to Prefect (for UI/backend integration)
        if self._prefect_logger:
            getattr(self._prefect_logger, level)(message, **kwargs)

        # Log to Loguru (for enhanced local logging)
        getattr(loguru_logger, level)(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log info message."""
        self._log_to_both("info", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log debug message."""
        self._log_to_both("debug", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log warning message."""
        self._log_to_both("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log error message."""
        self._log_to_both("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log critical message."""
        self._log_to_both("critical", message, **kwargs)

    def success(self, message: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Log success message (Loguru-specific level)."""
        # Use info for Prefect, success for Loguru
        if self._prefect_logger:
            self._prefect_logger.info(message, **kwargs)
        loguru_logger.success(message, **kwargs)


# Global hybrid logger instance
hybrid_logger = HybridLogger()


def get_hybrid_logger() -> HybridLogger:
    """Get the global hybrid logger instance."""
    return hybrid_logger


def refresh_logger() -> HybridLogger:
    """Refresh logger to pick up new Prefect context."""
    global hybrid_logger
    hybrid_logger = HybridLogger()
    return hybrid_logger
