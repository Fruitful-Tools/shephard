"""Test mock services."""

import pytest

from shepard_pipeline.services.mock_apis import (
    MockMistralService,
    MockOpenAIService,
    MockSupabaseService,
    MockVoxtralService,
    MockYouTubeService,
)


class TestMockYouTubeService:
    """Test MockYouTubeService."""

    @pytest.mark.asyncio
    async def test_download_audio(self) -> None:
        """Test YouTube audio download."""
        service = MockYouTubeService()

        result = await service.download_audio(
            "https://www.youtube.com/watch?v=test123", "/tmp/output.mp3"
        )

        assert "title" in result
        assert "duration" in result
        assert "file_path" in result
        assert result["file_path"] == "/tmp/output.mp3"
        assert result["format"] == "mp3"
        assert isinstance(result["duration"], int)
        assert result["duration"] > 0


class TestMockVoxtralService:
    """Test MockVoxtralService."""

    @pytest.mark.asyncio
    async def test_transcribe_chunk(self) -> None:
        """Test audio transcription."""
        service = MockVoxtralService()

        result = await service.transcribe_chunk("/tmp/audio_chunk_1.mp3", "zh-TW")

        assert result.chunk_id == "audio_chunk_1"
        assert isinstance(result.raw_text, str)
        assert len(result.raw_text) > 0
        assert 0.0 <= result.confidence <= 1.0
        assert result.language == "zh-TW"
        assert isinstance(result.timestamps, list)


class TestMockMistralService:
    """Test MockMistralService."""

    @pytest.mark.asyncio
    async def test_correct_text(self) -> None:
        """Test text correction."""
        service = MockMistralService()

        original_text = "這是測試文字"
        result = await service.correct_text(original_text, "zh-TW", "mistral-medium")

        assert result.original_text == original_text
        assert isinstance(result.corrected_text, str)
        assert len(result.corrected_text) > 0
        assert result.language == "zh-TW"
        assert result.model_used == "mistral-medium"
        # Should end with punctuation
        assert result.corrected_text.endswith(("。", "！", "？"))


class TestMockOpenAIService:
    """Test MockOpenAIService."""

    @pytest.mark.asyncio
    async def test_summarize_text(self) -> None:
        """Test text summarization."""
        service = MockOpenAIService()

        result = await service.summarize_text(
            "這是一段很長的測試文字，需要被總結成較短的摘要。", model="gpt-4"
        )

        assert isinstance(result.summary, str)
        assert len(result.summary) > 0
        assert result.word_count > 0
        assert result.model_used == "gpt-4"

    @pytest.mark.asyncio
    async def test_summarize_with_word_limit(self) -> None:
        """Test summarization with word limit."""
        service = MockOpenAIService()

        result = await service.summarize_text(
            "長文字測試內容", word_limit=5, model="gpt-4"
        )

        # Should respect word limit (approximately)
        word_count = len(result.summary.split())
        assert word_count <= 7  # Allow some flexibility

    @pytest.mark.asyncio
    async def test_summarize_with_instructions(self) -> None:
        """Test summarization with custom instructions."""
        service = MockOpenAIService()

        instructions = "請重點關注技術細節"
        result = await service.summarize_text(
            "測試文字", instructions=instructions, model="gpt-4"
        )

        assert result.custom_instructions == instructions


class TestMockSupabaseService:
    """Test MockSupabaseService."""

    @pytest.mark.asyncio
    async def test_create_job_record(self) -> None:
        """Test job record creation."""
        service = MockSupabaseService()

        job_data = {
            "user_id": "test_user",
            "entry_point": "youtube",
            "status": "pending",
        }

        job_id = await service.create_job_record(job_data)

        assert isinstance(job_id, str)
        assert len(job_id) > 0

        # Should be stored in mock database
        assert job_id in service.jobs_db
        stored_job = service.jobs_db[job_id]
        assert stored_job["user_id"] == "test_user"
        assert stored_job["status"] == "pending"

    @pytest.mark.asyncio
    async def test_update_job_status(self) -> None:
        """Test job status update."""
        service = MockSupabaseService()

        # Create job first
        job_id = await service.create_job_record({"status": "pending"})

        # Update status
        await service.update_job_status(job_id, "running", progress=50)

        stored_job = service.jobs_db[job_id]
        assert stored_job["status"] == "running"
        assert stored_job["progress"] == 50
        assert "updated_at" in stored_job

    @pytest.mark.asyncio
    async def test_get_job(self) -> None:
        """Test job retrieval."""
        service = MockSupabaseService()

        # Create job
        job_id = await service.create_job_record({"user_id": "test_user"})

        # Retrieve job
        job = await service.get_job(job_id)

        assert job is not None
        assert job["id"] == job_id
        assert job["user_id"] == "test_user"

        # Non-existent job
        non_existent = await service.get_job("fake_id")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_check_user_quota(self) -> None:
        """Test user quota check."""
        service = MockSupabaseService()

        quota = await service.check_user_quota("test_user")

        assert "daily_quota_remaining" in quota
        assert "credits_remaining" in quota
        assert "total_jobs_today" in quota

        assert isinstance(quota["daily_quota_remaining"], int)
        assert isinstance(quota["credits_remaining"], int)
        assert isinstance(quota["total_jobs_today"], int)

        assert quota["daily_quota_remaining"] >= 0
        assert quota["credits_remaining"] >= 0
        assert quota["total_jobs_today"] >= 0
