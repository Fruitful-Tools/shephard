"""Pytest configuration and fixtures."""

from collections.abc import Generator
from pathlib import Path
import tempfile
from unittest.mock import AsyncMock
from uuid import uuid4

from prefect.testing.utilities import prefect_test_harness
from pydantic import HttpUrl
import pytest

from shepherd_pipeline.models.pipeline import (
    CorrectionResult,
    PipelineInput,
    SummaryResult,
    TranscriptionResult,
)


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture() -> Generator[None, None, None]:
    """Set up Prefect test harness for all tests."""
    with prefect_test_harness():
        yield


@pytest.fixture
def temp_audio_file() -> Generator[str, None, None]:
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake audio data")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def sample_youtube_input() -> PipelineInput:
    """Sample YouTube pipeline input."""
    return PipelineInput(
        youtube_url=HttpUrl("https://www.youtube.com/watch?v=test123"),
        user_id="test_user",
        chunk_size_minutes=5,
        target_language="zh-TW",
        summary_instructions="Test summary instructions",
        summary_word_limit=100,
    )


@pytest.fixture
def mock_transcription_result() -> TranscriptionResult:
    """Mock transcription result."""
    return TranscriptionResult(
        raw_text="這是測試轉錄文字",
        language="zh-TW",
        model="voxtral-v1",
    )


@pytest.fixture
def mock_correction_result() -> CorrectionResult:
    """Mock correction result."""
    return CorrectionResult(
        original_text="這是測試轉錄文字",
        corrected_text="這是測試轉錄文字。",
        language="zh-TW",
        model="mistral-medium",
    )


@pytest.fixture
def mock_summary_result() -> SummaryResult:
    """Mock summary result."""
    return SummaryResult(
        summary="這是一個測試摘要，總結了輸入文字的主要內容。",
        word_count=25,
        model="gpt-4",
        custom_instructions="Test instructions",
    )


@pytest.fixture
def mock_youtube_service() -> AsyncMock:
    """Mock YouTube service."""
    service = AsyncMock()
    service.download_audio.return_value = {
        "title": "Test Video",
        "duration": 1800,  # 30 minutes
        "file_path": "/tmp/test_video.mp3",
        "format": "mp3",
        "sample_rate": 44100,
        "file_size": 1024000,
    }
    return service


@pytest.fixture
def mock_mistral_service(mock_correction_result: CorrectionResult) -> AsyncMock:
    """Mock Mistral correction service."""
    service = AsyncMock()
    service.correct_text.return_value = mock_correction_result
    return service


@pytest.fixture
def mock_openai_service(mock_summary_result: SummaryResult) -> AsyncMock:
    """Mock OpenAI summarization service."""
    service = AsyncMock()
    service.summarize_text.return_value = mock_summary_result
    return service


@pytest.fixture
def mock_supabase_service() -> AsyncMock:
    """Mock Supabase database service."""
    service = AsyncMock()
    service.create_job_record.return_value = str(uuid4())
    service.update_job_status.return_value = None
    service.get_job.return_value = {"id": "test_job", "status": "pending"}
    service.check_user_quota.return_value = {
        "daily_quota_remaining": 5,
        "credits_remaining": 10,
        "total_jobs_today": 1,
    }
    return service
