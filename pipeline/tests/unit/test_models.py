"""Test Pydantic models."""

from uuid import UUID

from pydantic import HttpUrl, ValidationError
import pytest

from shepard_pipeline.models.pipeline import (
    EntryPointType,
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
            entry_point=EntryPointType.YOUTUBE,
            youtube_url=HttpUrl("https://www.youtube.com/watch?v=test123"),
            user_id="test_user",
        )

        assert input_data.entry_point == EntryPointType.YOUTUBE
        assert str(input_data.youtube_url) == "https://www.youtube.com/watch?v=test123"
        assert input_data.user_id == "test_user"
        assert isinstance(input_data.job_id, UUID)

    def test_youtube_input_missing_url(self) -> None:
        """Test YouTube input without URL raises validation error."""
        with pytest.raises(ValidationError):
            PipelineInput(entry_point=EntryPointType.YOUTUBE, user_id="test_user")

    def test_audio_input_valid(self) -> None:
        """Test valid audio file input."""
        input_data = PipelineInput(
            entry_point=EntryPointType.AUDIO_FILE,
            audio_file_path="/path/to/audio.mp3",
            user_id="test_user",
        )

        assert input_data.entry_point == EntryPointType.AUDIO_FILE
        assert input_data.audio_file_path == "/path/to/audio.mp3"

    def test_audio_input_missing_path(self) -> None:
        """Test audio input without file path raises validation error."""
        with pytest.raises(ValidationError):
            PipelineInput(entry_point=EntryPointType.AUDIO_FILE, user_id="test_user")

    def test_text_input_valid(self) -> None:
        """Test valid text input."""
        input_data = PipelineInput(
            entry_point=EntryPointType.TEXT,
            text_content="Test text content",
            user_id="test_user",
        )

        assert input_data.entry_point == EntryPointType.TEXT
        assert input_data.text_content == "Test text content"

    def test_text_input_missing_content(self) -> None:
        """Test text input without content raises validation error."""
        with pytest.raises(ValidationError):
            PipelineInput(entry_point=EntryPointType.TEXT, user_id="test_user")

    def test_chunk_size_validation(self) -> None:
        """Test chunk size validation."""
        # Valid chunk size
        input_data = PipelineInput(
            entry_point=EntryPointType.TEXT, text_content="Test", chunk_size_minutes=15
        )
        assert input_data.chunk_size_minutes == 15

        # Invalid chunk size (too small)
        with pytest.raises(ValidationError):
            PipelineInput(
                entry_point=EntryPointType.TEXT,
                text_content="Test",
                chunk_size_minutes=0,
            )

        # Invalid chunk size (too large)
        with pytest.raises(ValidationError):
            PipelineInput(
                entry_point=EntryPointType.TEXT,
                text_content="Test",
                chunk_size_minutes=40,
            )


class TestTranscriptionResult:
    """Test TranscriptionResult model."""

    def test_valid_transcription(self) -> None:
        """Test valid transcription result."""
        result = TranscriptionResult(
            chunk_id="chunk_1",
            raw_text="Test transcription",
            confidence=0.95,
            language="zh-TW",
        )

        assert result.chunk_id == "chunk_1"
        assert result.raw_text == "Test transcription"
        assert result.confidence == 0.95
        assert result.language == "zh-TW"
        assert result.timestamps == []

    def test_confidence_validation(self) -> None:
        """Test confidence score validation."""
        # Valid confidence
        result = TranscriptionResult(
            chunk_id="test", raw_text="Test", confidence=0.5, language="zh-TW"
        )
        assert result.confidence == 0.5

        # Invalid confidence (too low)
        with pytest.raises(ValidationError):
            TranscriptionResult(
                chunk_id="test", raw_text="Test", confidence=-0.1, language="zh-TW"
            )

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            TranscriptionResult(
                chunk_id="test", raw_text="Test", confidence=1.1, language="zh-TW"
            )


class TestPipelineResult:
    """Test PipelineResult model."""

    def test_is_complete_property(self) -> None:
        """Test is_complete property."""
        # Completed job
        result = PipelineResult(
            job_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=JobStatus.COMPLETED,
            entry_point=EntryPointType.TEXT,
        )
        assert result.is_complete is True

        # Failed job
        result.status = JobStatus.FAILED
        assert result.is_complete is True

        # Running job
        result.status = JobStatus.RUNNING
        assert result.is_complete is False

        # Pending job
        result.status = JobStatus.PENDING
        assert result.is_complete is False

    def test_duration_minutes_property(self) -> None:
        """Test duration_minutes property."""
        result = PipelineResult(
            job_id=UUID("12345678-1234-5678-1234-567812345678"),
            status=JobStatus.COMPLETED,
            entry_point=EntryPointType.TEXT,
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
            summary="Test summary content", word_count=3, model_used="gpt-4"
        )

        assert result.summary == "Test summary content"
        assert result.word_count == 3
        assert result.model_used == "gpt-4"
        assert result.custom_instructions is None

    def test_with_custom_instructions(self) -> None:
        """Test summary with custom instructions."""
        result = SummaryResult(
            summary="Test summary",
            word_count=2,
            model_used="gpt-4",
            custom_instructions="Custom test instructions",
        )

        assert result.custom_instructions == "Custom test instructions"
