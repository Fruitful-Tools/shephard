"""Mock external API services for local development."""

import asyncio
import random
import time
from typing import Any
from uuid import uuid4

from ..models.pipeline import CorrectionResult, SummaryResult, TranscriptionResult


class MockYouTubeService:
    """Mock YouTube download service."""

    async def download_audio(self, _url: str, output_path: str) -> dict[str, Any]:
        """Mock YouTube audio download."""
        await asyncio.sleep(2)  # Simulate download time

        # Mock video metadata
        duration = random.randint(300, 10800)  # 5 min to 3 hours

        return {
            "title": f"Sample Video {random.randint(1000, 9999)}",
            "duration": duration,
            "file_path": output_path,
            "format": "mp3",
            "sample_rate": 44100,
            "file_size": duration * 128 * 1024 // 8,  # Rough estimate for 128kbps
        }


class MockVoxtralService:
    """Mock Voxtral transcription service."""

    def __init__(self) -> None:
        self.sample_texts = [
            "這是一段關於人工智慧發展的討論",
            "在今天的演講中我們將探討機器學習的基本概念",
            "這個專案的目標是建立一個智能的語音識別系統",
            "讓我們來看看深度學習在自然語言處理中的應用",
            "感謝大家今天的參與，希望這次的分享對您有所幫助",
        ]

    async def transcribe_chunk(
        self, audio_chunk_path: str, language: str = "zh-TW"
    ) -> TranscriptionResult:
        """Mock audio transcription."""
        await asyncio.sleep(1.5)  # Simulate processing time

        chunk_id = audio_chunk_path.split("/")[-1].replace(".mp3", "")

        return TranscriptionResult(
            chunk_id=chunk_id,
            raw_text=random.choice(self.sample_texts),
            confidence=random.uniform(0.85, 0.98),
            language=language,
            timestamps=[
                {"start": 0.0, "end": 2.5, "text": "這是"},
                {"start": 2.5, "end": 5.0, "text": "一段關於"},
                {"start": 5.0, "end": 8.0, "text": "人工智慧的討論"},
            ],
        )


class MockMistralService:
    """Mock Mistral text correction service."""

    async def correct_text(
        self, text: str, target_language: str = "zh-TW", model: str = "mistral-medium"
    ) -> CorrectionResult:
        """Mock text correction and translation."""
        await asyncio.sleep(1.0)  # Simulate processing time

        # Simple mock correction (add punctuation, fix spacing)
        corrected = text.replace(" ", "").replace("，", "，").replace("。", "。")
        if not corrected.endswith(("。", "！", "？")):
            corrected += "。"

        return CorrectionResult(
            chunk_id=str(uuid4()),
            original_text=text,
            corrected_text=corrected,
            language=target_language,
            model_used=model,
        )


class MockOpenAIService:
    """Mock OpenAI summarization service."""

    def __init__(self) -> None:
        self.sample_summaries = [
            "本次討論主要聚焦於人工智慧技術的最新發展趨勢，包括機器學習演算法的改進以及在各行業的實際應用案例。",
            "演講者詳細介紹了深度學習在自然語言處理領域的突破性進展，特別強調了預訓練模型的重要性。",
            "此專案旨在開發先進的語音識別系統，結合最新的神經網路架構來提升識別準確度和處理效率。",
            "內容涵蓋了AI技術的基礎理論、實際應用場景，以及未來發展方向的深入分析。",
        ]

    async def summarize_text(
        self,
        _text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "gpt-4",
    ) -> SummaryResult:
        """Mock text summarization."""
        await asyncio.sleep(2.0)  # Simulate processing time

        summary = random.choice(self.sample_summaries)

        # Adjust length based on word limit
        if word_limit:
            words = summary.split()
            if len(words) > word_limit:
                summary = " ".join(words[:word_limit]) + "..."

        return SummaryResult(
            summary=summary,
            word_count=len(summary.split()),
            model_used=model,
            custom_instructions=instructions,
        )


class MockSupabaseService:
    """Mock Supabase database service."""

    def __init__(self) -> None:
        self.jobs_db: dict[str, dict[str, Any]] = {}  # In-memory job storage

    async def create_job_record(self, job_data: dict[str, Any]) -> str:
        """Create a new job record."""
        job_id = str(uuid4())
        self.jobs_db[job_id] = {
            **job_data,
            "id": job_id,
            "created_at": time.time(),
            "status": "pending",
        }
        return job_id

    async def update_job_status(self, job_id: str, status: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Update job status and metadata."""
        if job_id in self.jobs_db:
            self.jobs_db[job_id].update(
                {"status": status, "updated_at": time.time(), **kwargs}
            )

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get job by ID."""
        return self.jobs_db.get(job_id)

    async def check_user_quota(self, _user_id: str) -> dict[str, int]:
        """Check user's remaining quota and credits."""
        return {
            "daily_quota_remaining": random.randint(0, 5),
            "credits_remaining": random.randint(1, 50),
            "total_jobs_today": random.randint(0, 3),
        }
