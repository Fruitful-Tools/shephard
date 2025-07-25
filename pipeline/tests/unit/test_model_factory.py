"""Test model factory."""

from shepherd_pipeline.services.llm_provider import (
    MistralService,
    MockAIService,
    OpenAIService,
)
from shepherd_pipeline.services.model_factory import AIProvider, ModelFactory, TaskType


class TestModelFactory:
    """Test ModelFactory."""

    def test_get_provider_for_model_openai(self) -> None:
        """Test OpenAI model provider detection."""
        assert ModelFactory.get_provider_for_model("gpt-4.1-nano") == AIProvider.OPENAI
        assert ModelFactory.get_provider_for_model("gpt-4o-mini") == AIProvider.OPENAI
        assert ModelFactory.get_provider_for_model("gpt-4.1-mini") == AIProvider.OPENAI

    def test_get_provider_for_model_mistral(self) -> None:
        """Test Mistral model provider detection."""
        assert (
            ModelFactory.get_provider_for_model("mistral-small-latest")
            == AIProvider.MISTRAL
        )
        assert (
            ModelFactory.get_provider_for_model("mistral-medium-2505")
            == AIProvider.MISTRAL
        )
        assert (
            ModelFactory.get_provider_for_model("voxtral-mini-latest")
            == AIProvider.MISTRAL
        )

    def test_get_provider_for_model_unknown(self) -> None:
        """Test unknown model defaults to Mistral."""
        assert (
            ModelFactory.get_provider_for_model("unknown-model") == AIProvider.MISTRAL
        )

    def test_create_text_processor_mock(self) -> None:
        """Test creating mock text processor."""
        processor = ModelFactory.create_text_processor("mock-model")
        assert isinstance(processor, MockAIService)

    def test_create_text_processor_openai(self) -> None:
        """Test creating OpenAI text processor."""
        processor = ModelFactory.create_text_processor("gpt-4o-mini")
        assert isinstance(processor, OpenAIService)

    def test_create_text_processor_mistral(self) -> None:
        """Test creating Mistral text processor."""
        processor = ModelFactory.create_text_processor("mistral-small-latest")
        assert isinstance(processor, MistralService)

    def test_create_summarization_service_mock(self) -> None:
        """Test creating mock summarization service."""
        service = ModelFactory.create_summarization_service("mock-model")
        assert isinstance(service, MockAIService)

    def test_create_summarization_service_openai(self) -> None:
        """Test creating OpenAI summarization service."""
        service = ModelFactory.create_summarization_service("gpt-4o-mini")
        assert isinstance(service, OpenAIService)

    def test_create_summarization_service_mistral(self) -> None:
        """Test creating Mistral summarization service."""
        service = ModelFactory.create_summarization_service("mistral-small-latest")
        assert isinstance(service, MistralService)

    def test_get_supported_models(self) -> None:
        """Test getting supported models."""
        models = ModelFactory.get_supported_models()

        assert AIProvider.OPENAI in models
        assert AIProvider.MISTRAL in models
        assert AIProvider.MOCK in models

        assert "gpt-4o-mini" in models[AIProvider.OPENAI]
        assert "mistral-small-latest" in models[AIProvider.MISTRAL]
        assert "mock-model" in models[AIProvider.MOCK]

    def test_validate_model_valid(self) -> None:
        """Test validating valid models."""
        assert ModelFactory.validate_model_simple("gpt-4o-mini") is True
        assert ModelFactory.validate_model_simple("mistral-small-latest") is True
        assert ModelFactory.validate_model_simple("mock-model") is True

    def test_validate_model_invalid(self) -> None:
        """Test validating invalid models."""
        assert ModelFactory.validate_model_simple("unknown-model") is False

    def test_get_default_model_for_provider(self) -> None:
        """Test getting default models for providers."""
        assert (
            ModelFactory.get_default_model_for_provider(AIProvider.OPENAI, "text")
            == "gpt-4o-mini"
        )
        assert (
            ModelFactory.get_default_model_for_provider(AIProvider.MISTRAL, "text")
            == "mistral-small-latest"
        )
        assert (
            ModelFactory.get_default_model_for_provider(AIProvider.MOCK, "text")
            == "mock-model"
        )
        assert (
            ModelFactory.get_default_model_for_provider(
                AIProvider.OPENAI, "transcription"
            )
            == "gpt-4o-mini-transcribe"
        )
        assert (
            ModelFactory.get_default_model_for_provider(
                AIProvider.MISTRAL, "transcription"
            )
            == "voxtral-mini-latest"
        )

    def test_validate_model_with_task_type(self) -> None:
        """Test new validate_model method with task types."""
        # Valid combinations
        assert (
            ModelFactory.validate_model(
                AIProvider.OPENAI, "gpt-4o-mini", TaskType.CORRECTION
            )
            is True
        )
        assert (
            ModelFactory.validate_model(
                AIProvider.MISTRAL, "voxtral-mini-latest", TaskType.TRANSCRIPTION
            )
            is True
        )
        assert (
            ModelFactory.validate_model(None, "gpt-4o-mini", TaskType.CORRECTION)
            is True
        )

        # Invalid combinations
        assert (
            ModelFactory.validate_model(
                AIProvider.OPENAI, "voxtral-mini-latest", TaskType.TRANSCRIPTION
            )
            is False
        )
        assert (
            ModelFactory.validate_model(
                AIProvider.MISTRAL, "gpt-4o-mini", TaskType.CORRECTION
            )
            is False
        )
        assert (
            ModelFactory.validate_model(
                AIProvider.OPENAI, "unknown-model", TaskType.CORRECTION
            )
            is False
        )

    def test_get_models_by_provider_and_task(self) -> None:
        """Test getting models by provider and task type."""
        openai_correction = ModelFactory.get_models(
            AIProvider.OPENAI, TaskType.CORRECTION
        )
        assert "gpt-4o-mini" in openai_correction
        assert "gpt-4.1-nano" in openai_correction
        assert "voxtral-mini-latest" not in openai_correction

        mistral_transcription = ModelFactory.get_models(
            AIProvider.MISTRAL, TaskType.TRANSCRIPTION
        )
        assert "voxtral-mini-latest" in mistral_transcription
        assert "mistral-small-latest" not in mistral_transcription

    def test_create_transcription_service_mock(self) -> None:
        """Test creating mock transcription service."""
        service = ModelFactory.create_transcription_service("mock-model")
        assert isinstance(service, MockAIService)

    def test_create_transcription_service_openai(self) -> None:
        """Test creating OpenAI transcription service."""
        service = ModelFactory.create_transcription_service("gpt-4o-mini-transcribe")
        assert isinstance(service, OpenAIService)

    def test_create_transcription_service_mistral_voxtral(self) -> None:
        """Test creating Mistral transcription service (unified with Voxtral)."""
        service = ModelFactory.create_transcription_service("voxtral-mini-latest")
        # Should return unified MistralService with transcription capability
        assert isinstance(service, MistralService)
        assert hasattr(service, "transcribe_audio")
