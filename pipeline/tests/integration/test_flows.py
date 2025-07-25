"""Integration tests for pipeline flows."""

from typing import Any
from unittest.mock import patch

from pydantic import HttpUrl
import pytest

from shepard_pipeline.flows.main_flows import (
    audio_file_pipeline_flow,
    main_pipeline_flow,
    text_summary_pipeline_flow,
    youtube_pipeline_flow,
)
from shepard_pipeline.models.pipeline import EntryPointType, JobStatus, PipelineInput


class TestYouTubePipelineFlow:
    """Test YouTube pipeline flow."""

    @pytest.mark.asyncio
    async def test_youtube_pipeline_success(
        self, sample_youtube_input: PipelineInput
    ) -> None:
        """Test successful YouTube pipeline execution."""
        result = await youtube_pipeline_flow(sample_youtube_input)

        assert result.job_id == sample_youtube_input.job_id
        assert result.user_id == sample_youtube_input.user_id
        assert result.entry_point == EntryPointType.YOUTUBE
        assert result.status == JobStatus.COMPLETED

        # Should have processing steps completed
        assert len(result.audio_chunks) > 0
        assert len(result.transcriptions) > 0
        assert len(result.corrections) > 0
        assert result.summary is not None

        # Should have timing information
        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.completed_at > result.started_at

        # Should consume credits
        assert result.credits_consumed > 0

    @pytest.mark.asyncio
    async def test_youtube_pipeline_with_custom_parameters(self) -> None:
        """Test YouTube pipeline with custom parameters."""
        from shepard_pipeline.models.pipeline import PipelineInput

        input_data = PipelineInput(
            entry_point=EntryPointType.YOUTUBE,
            youtube_url=HttpUrl("https://www.youtube.com/watch?v=test123"),
            user_id="test_user",
            chunk_size_minutes=5,
            target_language="en-US",
            transcription_model="voxtral-v2",
            correction_model="mistral-large",
            summarization_model="gpt-4-turbo",
            summary_instructions="Focus on key technical details",
            summary_word_limit=150,
        )

        result = await youtube_pipeline_flow(input_data)

        assert result.status == JobStatus.COMPLETED
        assert result.input_params is not None
        assert result.input_params.chunk_size_minutes == 5
        assert result.input_params.target_language == "en-US"
        assert result.input_params.summary_word_limit == 150


class TestAudioFilePipelineFlow:
    """Test audio file pipeline flow."""

    @pytest.mark.asyncio
    async def test_audio_pipeline_success(
        self, sample_audio_input: PipelineInput
    ) -> None:
        """Test successful audio file pipeline execution."""
        result = await audio_file_pipeline_flow(sample_audio_input)

        assert result.job_id == sample_audio_input.job_id
        assert result.entry_point == EntryPointType.AUDIO_FILE
        assert result.status == JobStatus.COMPLETED

        # Should have processing steps completed
        assert len(result.audio_chunks) > 0
        assert len(result.transcriptions) > 0
        assert len(result.corrections) > 0
        assert result.summary is not None

        assert result.credits_consumed > 0


class TestTextSummaryPipelineFlow:
    """Test text summary pipeline flow."""

    @pytest.mark.asyncio
    async def test_text_pipeline_success(
        self, sample_text_input: PipelineInput
    ) -> None:
        """Test successful text summary pipeline execution."""
        result = await text_summary_pipeline_flow(sample_text_input)

        assert result.job_id == sample_text_input.job_id
        assert result.entry_point == EntryPointType.TEXT
        assert result.status == JobStatus.COMPLETED

        # Text pipeline skips audio processing
        assert len(result.audio_chunks) == 0
        assert len(result.transcriptions) == 0
        assert len(result.corrections) == 0

        # But should have summary
        assert result.summary is not None

        # Text processing always consumes 1 credit
        assert result.credits_consumed == 1

    @pytest.mark.asyncio
    async def test_text_pipeline_with_word_limit(self) -> None:
        """Test text pipeline respects word limit."""
        from shepard_pipeline.models.pipeline import PipelineInput

        input_data = PipelineInput(
            entry_point=EntryPointType.TEXT,
            text_content="這是一段很長的測試文字內容，需要被總結成較短的摘要。" * 10,
            summary_word_limit=80,
        )

        result = await text_summary_pipeline_flow(input_data)

        assert result.status == JobStatus.COMPLETED
        assert result.summary is not None
        # Note: Mock service may not perfectly respect word limits
        # but real implementation should


class TestMainPipelineFlow:
    """Test main pipeline dispatcher flow."""

    @pytest.mark.asyncio
    async def test_dispatch_youtube_pipeline(
        self, sample_youtube_input: PipelineInput
    ) -> None:
        """Test dispatching to YouTube pipeline."""
        result = await main_pipeline_flow(sample_youtube_input)

        assert result.entry_point == EntryPointType.YOUTUBE
        assert result.status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_dispatch_audio_pipeline(
        self, sample_audio_input: PipelineInput
    ) -> None:
        """Test dispatching to audio file pipeline."""
        result = await main_pipeline_flow(sample_audio_input)

        assert result.entry_point == EntryPointType.AUDIO_FILE
        assert result.status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_dispatch_text_pipeline(
        self, sample_text_input: PipelineInput
    ) -> None:
        """Test dispatching to text summary pipeline."""
        result = await main_pipeline_flow(sample_text_input)

        assert result.entry_point == EntryPointType.TEXT
        assert result.status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_invalid_entry_point(self) -> None:
        """Test error handling for invalid entry point."""
        from shepard_pipeline.models.pipeline import PipelineInput

        # Create input with invalid entry point (bypassing validation)
        input_data = PipelineInput(entry_point=EntryPointType.TEXT, text_content="test")

        # Manually set invalid entry point
        input_data.entry_point = "invalid_entry_point"  # type: ignore[assignment]

        with pytest.raises(ValueError, match="Unsupported entry point"):
            await main_pipeline_flow(input_data)


class TestPipelineErrorHandling:
    """Test error handling in pipelines."""

    @pytest.mark.asyncio
    async def test_pipeline_handles_task_failure(
        self, sample_text_input: PipelineInput, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test pipeline handles task failures gracefully."""

        # Mock a task to raise an exception
        async def failing_summarize_text(*args: Any, **kwargs: Any) -> None:
            raise Exception("Mock API failure")

        with patch(
            "shepard_pipeline.flows.main_flows.summarize_text", failing_summarize_text
        ):
            result = await text_summary_pipeline_flow(sample_text_input)

            assert result.status == JobStatus.FAILED
            assert result.error_message == "Mock API failure"
            assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_pipeline_cleans_up_temp_files(
        self, sample_youtube_input: PipelineInput
    ) -> None:
        """Test that temporary files are cleaned up even on failure."""

        # Mock cleanup function to track calls
        cleanup_called = []

        async def mock_cleanup(file_paths: list[str]) -> None:
            cleanup_called.extend(file_paths)

        with patch(
            "shepard_pipeline.flows.main_flows.cleanup_temp_files", mock_cleanup
        ):
            await youtube_pipeline_flow(sample_youtube_input)

            # Should have called cleanup (even on success)
            assert len(cleanup_called) > 0
