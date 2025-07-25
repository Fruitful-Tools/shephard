"""Test Pydantic models."""

from uuid import UUID

from pydantic import HttpUrl, ValidationError
import pytest

from shepherd_pipeline.models.pipeline import (
    JobStatus,
    PipelineInput,
    PipelineResult,
    SummaryResult,
    TranscriptionResult,
)


class TestPipelineInput:
    """Test PipelineInput model."""

    def test_youtube_input_valid(self) -> None:
        """Test valid YouTube input."""
        input_data = PipelineInput(
            youtube_url=HttpUrl("https://www.youtube.com/watch?v=test123"),
            user_id="test_user",
        )

        assert str(input_data.youtube_url) == "https://www.youtube.com/watch?v=test123"
        assert input_data.user_id == "test_user"
        assert isinstance(input_data.job_id, UUID)

    def test_youtube_input_missing_url(self) -> None:
        """Test YouTube input without URL is valid - inputs are optional."""
        # PipelineInput now accepts multiple input types, all optional
        input_data = PipelineInput(user_id="test_user")
        assert input_data.user_id == "test_user"
        assert input_data.youtube_url is None
        assert isinstance(input_data.job_id, UUID)

    def test_chunk_size_validation(self) -> None:
        """Test chunk size validation."""
        # Valid chunk size
        input_data = PipelineInput(text_content="Test", chunk_size_minutes=15)
        assert input_data.chunk_size_minutes == 15

        # Invalid chunk size (too small)
        with pytest.raises(ValidationError):
            PipelineInput(
                text_content="Test",
                chunk_size_minutes=0,
            )

        # Invalid chunk size (too large)
        with pytest.raises(ValidationError):
            PipelineInput(
                text_content="Test",
                chunk_size_minutes=40,
            )


class TestTranscriptionResult:
    """Test TranscriptionResult model."""

    def test_valid_transcription(self) -> None:
        """Test valid transcription result."""
        result = TranscriptionResult(
            raw_text="Test transcription",
            language="zh-TW",
            model="voxtral-v1",
        )

        assert result.raw_text == "Test transcription"
        assert result.language == "zh-TW"
        assert result.model == "voxtral-v1"
        assert result.failure_reason is None

    def test_with_failure_reason(self) -> None:
        """Test transcription with failure reason."""
        result = TranscriptionResult(
            raw_text="",
            language="zh-TW",
            model="voxtral-v1",
            failure_reason="Audio quality too low",
        )
        assert result.raw_text == ""
        assert result.failure_reason == "Audio quality too low"


class TestPipelineResult:
    """Test PipelineResult model."""

    def test_is_complete_property(self) -> None:
        """Test is_complete property."""
        # Completed job
        result = PipelineResult(
            job_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=JobStatus.COMPLETED,
        )
        assert result.is_complete is True

        # Failed job
        result.status = JobStatus.FAILED
        assert result.is_complete is True

        # Cancelled job
        result.status = JobStatus.CANCELLED
        assert result.is_complete is True

        # Running job
        result.status = JobStatus.RUNNING
        assert result.is_complete is False

        # Pending job
        result.status = JobStatus.PENDING  # type: ignore[unreachable]
        assert result.is_complete is False

    def test_duration_minutes_property(self) -> None:
        """Test duration_minutes property."""
        result = PipelineResult(
            job_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=JobStatus.COMPLETED,
        )

        # No processing duration
        assert result.duration_minutes is None

        # With processing duration (120 seconds = 2 minutes)
        result.processing_duration = 120.0
        assert result.duration_minutes == 2.0


class TestSummaryResult:
    """Test SummaryResult model."""

    def test_valid_summary(self) -> None:
        """Test valid summary result."""
        result = SummaryResult(
            summary="Test summary content", word_count=3, model="gpt-4"
        )

        assert result.summary == "Test summary content"
        assert result.word_count == 3
        assert result.model == "gpt-4"
        assert result.custom_instructions is None

    def test_with_custom_instructions(self) -> None:
        """Test summary with custom instructions."""
        result = SummaryResult(
            summary="Test summary",
            word_count=2,
            model="gpt-4",
            custom_instructions="Custom test instructions",
        )

        assert result.custom_instructions == "Custom test instructions"
