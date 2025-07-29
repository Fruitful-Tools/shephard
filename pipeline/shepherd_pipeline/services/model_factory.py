"""Model factory for creating AI service instances based on model configuration."""

from enum import Enum
from typing import Any, Protocol

from .llm_provider.schema import CorrectionResult, SummaryResult, TranscriptionResult


class AIProvider(str, Enum):
    """AI service providers."""

    OPENAI = "openai"
    MISTRAL = "mistral"
    MOCK = "mock"


class TaskType(str, Enum):
    """Task types for AI models."""

    TRANSCRIPTION = "transcription"
    CORRECTION = "correction"
    SUMMARIZATION = "summarization"


class TextProcessorProtocol(Protocol):
    """Protocol for text processing services."""

    async def correct_text(
        self, text: str, target_language: str = "zh-TW", model: str = "default"
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
        """Generate summary from text."""
        ...


class TranscriptionProtocol(Protocol):
    """Protocol for transcription services."""

    async def transcribe_audio(
        self, audio_file_path: str, language: str = "zh"
    ) -> TranscriptionResult:
        """Transcribe audio to text."""
        ...


class ModelFactory:
    """Factory for creating AI service instances based on model configuration."""

    # Model configuration with provider and supported tasks
    MODEL_CONFIG: dict[str, dict[str, Any]] = {
        # OpenAI models
        "gpt-4.1-nano": {
            "provider": AIProvider.OPENAI,
            "tasks": [TaskType.CORRECTION, TaskType.SUMMARIZATION],
        },
        "gpt-4o-mini": {
            "provider": AIProvider.OPENAI,
            "tasks": [TaskType.CORRECTION, TaskType.SUMMARIZATION],
        },
        "gpt-4.1-mini": {
            "provider": AIProvider.OPENAI,
            "tasks": [TaskType.CORRECTION, TaskType.SUMMARIZATION],
        },
        "gpt-4o-mini-transcribe": {
            "provider": AIProvider.OPENAI,
            "tasks": [TaskType.TRANSCRIPTION],
        },
        "gpt-4o-transcribe": {
            "provider": AIProvider.OPENAI,
            "tasks": [TaskType.TRANSCRIPTION],
        },
        # Mistral models
        "mistral-small-latest": {
            "provider": AIProvider.MISTRAL,
            "tasks": [TaskType.CORRECTION, TaskType.SUMMARIZATION],
        },
        "mistral-medium-2505": {
            "provider": AIProvider.MISTRAL,
            "tasks": [TaskType.CORRECTION, TaskType.SUMMARIZATION],
        },
        "voxtral-mini-latest": {
            "provider": AIProvider.MISTRAL,
            "tasks": [TaskType.TRANSCRIPTION],
        },
        "voxtral-small-latest": {
            "provider": AIProvider.MISTRAL,
            "tasks": [TaskType.TRANSCRIPTION],
        },
        # Mock model
        "mock-model": {
            "provider": AIProvider.MOCK,
            "tasks": [
                TaskType.TRANSCRIPTION,
                TaskType.CORRECTION,
                TaskType.SUMMARIZATION,
            ],
        },
    }

    # Legacy provider mapping for backward compatibility
    MODEL_PROVIDERS: dict[str, AIProvider] = {
        model: config["provider"] for model, config in MODEL_CONFIG.items()
    }

    # Default models for each provider and task
    DEFAULT_MODELS: dict[tuple[AIProvider, TaskType], str] = {
        (AIProvider.OPENAI, TaskType.TRANSCRIPTION): "gpt-4o-mini-transcribe",
        (AIProvider.OPENAI, TaskType.CORRECTION): "gpt-4o-mini",
        (AIProvider.OPENAI, TaskType.SUMMARIZATION): "gpt-4o-mini",
        (AIProvider.MISTRAL, TaskType.TRANSCRIPTION): "voxtral-mini-latest",
        (AIProvider.MISTRAL, TaskType.CORRECTION): "mistral-small-latest",
        (AIProvider.MISTRAL, TaskType.SUMMARIZATION): "mistral-small-latest",
        (AIProvider.MOCK, TaskType.TRANSCRIPTION): "mock-model",
        (AIProvider.MOCK, TaskType.CORRECTION): "mock-model",
        (AIProvider.MOCK, TaskType.SUMMARIZATION): "mock-model",
    }

    @classmethod
    def get_provider_for_model(cls, model: str) -> AIProvider:
        """Determine the provider for a given model."""
        return cls.MODEL_PROVIDERS.get(model, AIProvider.MISTRAL)

    @classmethod
    def validate_model(
        cls, provider: AIProvider | None, model: str, task_type: TaskType
    ) -> bool:
        """Validate if a model is supported for a specific provider and task type."""
        if model not in cls.MODEL_CONFIG:
            return False

        config = cls.MODEL_CONFIG[model]

        # Check if provider matches (if provided)
        if provider is not None and config["provider"] != provider:
            return False

        # Check if task is supported
        return task_type in config["tasks"]

    @classmethod
    def get_models(cls, provider: AIProvider, task_type: TaskType) -> list[str]:
        """Get all models for a specific provider and task type."""
        return [
            model
            for model, config in cls.MODEL_CONFIG.items()
            if config["provider"] == provider and task_type in config["tasks"]
        ]

    @classmethod
    def _create_service_instance(cls, provider: AIProvider) -> Any:  # noqa: ANN401
        """Create a service instance for the given provider."""
        if provider == AIProvider.MOCK:
            from .llm_provider.mock import MockAIService

            return MockAIService()
        elif provider == AIProvider.OPENAI:
            from .llm_provider.openai_service import OpenAIService

            return OpenAIService()
        elif provider == AIProvider.MISTRAL:
            from .llm_provider.mistral_service import MistralService

            return MistralService()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @classmethod
    def create_text_processor(cls, model: str) -> TextProcessorProtocol:
        """Create a text processing service instance based on model."""
        provider = cls.get_provider_for_model(model)
        return cls._create_service_instance(provider)

    @classmethod
    def create_summarization_service(cls, model: str) -> TextProcessorProtocol:
        """Create a summarization service instance based on model."""
        provider = cls.get_provider_for_model(model)
        return cls._create_service_instance(provider)

    @classmethod
    def get_supported_models(cls) -> dict[AIProvider, list[str]]:
        """Get all supported models grouped by provider."""
        models_by_provider: dict[AIProvider, list[str]] = {
            AIProvider.OPENAI: [],
            AIProvider.MISTRAL: [],
            AIProvider.MOCK: [],
        }

        for model, config in cls.MODEL_CONFIG.items():
            provider = config["provider"]
            models_by_provider[provider].append(model)

        return models_by_provider

    @classmethod
    def get_default_model_for_provider(
        cls, provider: AIProvider, task: TaskType | str
    ) -> str:
        """Get default model for a provider and task type."""
        if isinstance(task, TaskType):
            task_type = task
        else:
            # Legacy string support
            if task == "transcription":
                task_type = TaskType.TRANSCRIPTION
            else:
                task_type = TaskType.CORRECTION  # Default to correction for text tasks
        return cls.DEFAULT_MODELS.get((provider, task_type), "mock-model")

    @classmethod
    def validate_model_simple(cls, model: str) -> bool:
        """Legacy simple model validation for backward compatibility."""
        return model in cls.MODEL_CONFIG

    @classmethod
    def create_transcription_service(cls, model: str) -> TranscriptionProtocol:
        """Create a transcription service instance based on model."""
        provider = cls.get_provider_for_model(model)
        return cls._create_service_instance(provider)
