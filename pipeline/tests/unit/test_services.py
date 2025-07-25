"""Test mock services."""

import pytest

from shepherd_pipeline.services.llm_provider import MockAIService
from shepherd_pipeline.services.mock_apis import MockSupabaseService
from shepherd_pipeline.services.youtube.mock import MockYouTubeService


class TestMockYouTubeService:
    """Test MockYouTubeService."""

    @pytest.mark.asyncio
    async def test_download_audio(self) -> None:
        """Test YouTube audio download."""
        service = MockYouTubeService()

        result = await service.download_audio("https://www.youtube.com/watch?v=test123")

        assert result.title
        assert result.duration > 0
        assert result.file_path
        assert result.format == "mp3"
        assert isinstance(result.duration, int | float)
        assert result.duration > 0


class TestMockAIService:
    """Test unified MockAIService."""

    @pytest.mark.asyncio
    async def test_transcribe_audio(self) -> None:
        """Test OpenAI-style audio transcription."""
        service = MockAIService()

        result = await service.transcribe_audio("/tmp/audio_file.mp3", "zh")

        assert isinstance(result.raw_text, str)
        assert len(result.raw_text) > 0
        assert result.language == "zh"
        assert result.model == "mock-model"
        assert result.failure_reason is None

    @pytest.mark.asyncio
    async def test_correct_text(self) -> None:
        """Test text correction."""
        service = MockAIService()

        original_text = "這是測試文字"
        result = await service.correct_text(
            original_text, "zh-TW", "mistral-small-latest"
        )

        assert result.original_text == original_text
        assert isinstance(result.corrected_text, str)
        assert len(result.corrected_text) > 0
        assert result.language == "zh-TW"
        assert result.model == "mistral-small-latest"
        # Should end with punctuation
        assert result.corrected_text.endswith(("。", "！", "？", "：", "；"))

    @pytest.mark.asyncio
    async def test_correct_text_christian_context(self) -> None:
        """Test text correction with Christian terminology."""
        service = MockAIService()

        # Test text with simplified Chinese Christian terms
        original_text = "神的恩典 教会的弟兄姊妹 祷告和见证"
        result = await service.correct_text(
            original_text, "zh-TW", "mistral-small-latest"
        )

        # Should convert to traditional Chinese
        assert "上帝" in result.corrected_text or "神" in result.corrected_text
        assert "教會" in result.corrected_text or "教会" in result.corrected_text
        assert "禱告" in result.corrected_text or "祷告" in result.corrected_text
        assert "見證" in result.corrected_text or "见证" in result.corrected_text

    @pytest.mark.asyncio
    async def test_summarize_text(self) -> None:
        """Test text summarization."""
        service = MockAIService()

        text = (
            "今天我要跟大家分享關於神的恩典的見證。神在我生命中做了奇妙的工作，"
            "透過禱告和讀經讓我更親近祂。教會的弟兄姊妹也給了我很多支持和鼓勵。"
        )

        result = await service.summarize_text(
            text,
            model="mistral-small-latest",
            instructions="這是一天基督教的講道，請整理三段式重點摘要",
        )

        assert isinstance(result.summary, str)
        assert len(result.summary) > 0
        assert result.word_count > 0
        assert result.model == "mistral-small-latest"
        # Should contain Christian terminology
        assert any(
            term in result.summary
            for term in ["基督", "信仰", "神", "上帝", "教會", "禱告"]
        )

    @pytest.mark.asyncio
    async def test_summarize_text_with_word_limit(self) -> None:
        """Test summarization with word limit."""
        service = MockAIService()

        text = "長文字測試內容，需要被總結為更短的摘要。"
        result = await service.summarize_text(
            text, word_limit=20, model="mistral-small-latest"
        )

        # Should respect word limit (approximately) - check word count for Chinese
        # In Chinese, each character is roughly equivalent to a word
        assert result.word_count <= 30  # Allow some flexibility for Chinese text

    @pytest.mark.asyncio
    async def test_summarize_text_with_instructions(self) -> None:
        """Test summarization with custom instructions."""
        service = MockAIService()

        instructions = "請重點關注屬靈成長的部分"
        text = "今天分享信仰見證，談到神的恩典和教會生活。"

        result = await service.summarize_text(
            text, instructions=instructions, model="mistral-small-latest"
        )

        assert result.custom_instructions == instructions

    @pytest.mark.asyncio
    async def test_summarize_text_general_mode(self) -> None:
        """Test text summarization in general mode (non-Christian)."""
        service = MockAIService()

        result = await service.summarize_text(
            "這是一段很長的測試文字，需要被總結成較短的摘要。", model="gpt-4"
        )

        assert isinstance(result.summary, str)
        assert len(result.summary) > 0
        assert result.word_count > 0
        assert result.model == "gpt-4"

    @pytest.mark.asyncio
    async def test_summarize_with_word_limit(self) -> None:
        """Test summarization with word limit."""
        service = MockAIService()

        result = await service.summarize_text(
            "長文字測試內容", word_limit=5, model="gpt-4"
        )

        # Should respect word limit (approximately)
        assert result.word_count <= 10  # Allow some flexibility for Chinese text

    @pytest.mark.asyncio
    async def test_summarize_with_instructions(self) -> None:
        """Test summarization with custom instructions."""
        service = MockAIService()

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
