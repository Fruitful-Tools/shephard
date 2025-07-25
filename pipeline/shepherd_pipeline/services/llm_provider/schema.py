"""Common schemas and types for LLM provider services."""

from abc import ABC, abstractmethod
import logging
from typing import Protocol

from loguru import logger

from ...models.pipeline import CorrectionResult, SummaryResult, TranscriptionResult


class LLMServiceProtocol(Protocol):
    """Protocol defining the interface for LLM services."""

    async def transcribe_audio(
        self,
        audio_chunk_path: str,
        language: str = "zh",
        model: str = "default",
    ) -> TranscriptionResult:
        """Transcribe audio chunk to text."""
        ...

    async def correct_text(
        self,
        text: str,
        target_language: str = "zh-TW",
        model: str = "default",
    ) -> CorrectionResult:
        """Correct and enhance transcribed text."""
        ...

    async def summarize_text(
        self,
        text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "default",
    ) -> SummaryResult:
        """Generate summary of text."""
        ...


class BaseLLMService(ABC):
    """Abstract base class for LLM services."""

    logger: logging.Logger | logging.LoggerAdapter[logging.Logger]

    def __init__(self) -> None:
        try:
            from prefect import get_run_logger

            self.logger = get_run_logger()
        except Exception:
            self.logger = logger  # type: ignore[assignment]

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_chunk_path: str,
        language: str = "zh",
        model: str = "default",
    ) -> TranscriptionResult:
        """Transcribe audio chunk to text."""
        pass

    @abstractmethod
    async def correct_text(
        self,
        text: str,
        target_language: str = "zh-TW",
        model: str = "default",
    ) -> CorrectionResult:
        """Correct and enhance transcribed text."""
        pass

    @abstractmethod
    async def summarize_text(
        self,
        text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "default",
    ) -> SummaryResult:
        """Generate summary of text."""
        pass
