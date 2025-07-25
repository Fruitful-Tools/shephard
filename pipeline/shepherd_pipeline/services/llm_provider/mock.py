"""Mock LLM API services for local development."""

import random
import time
from typing import Any
from uuid import uuid4

from ...models.pipeline import CorrectionResult, SummaryResult, TranscriptionResult
from .schema import BaseLLMService


class MockAIService(BaseLLMService):
    """Unified mock AI service for transcription, correction, and summarization."""

    def __init__(self) -> None:
        super().__init__()
        # Sample transcription texts
        self.sample_texts = [
            "今天我要跟大家分享關於神的恩典的見證 神在我生命中做了奇妙的工作",
            "我們一起來讀詩篇二十三篇 耶和華是我的牧者 我必不致缺乏",
            "弟兄姊妹們 讓我們一起來禱告 求神賜給我們智慧和力量",
            "聖經告訴我們 神愛世人 甚至將他的獨生子賜給他們",
            "在這個困難的時刻 我們要倚靠聖靈的能力 相信神的計劃是美好的",
            "教會是神的家 我們要彼此相愛 彼此服事",
            "感謝主的恩典 讓我們今天能夠聚集在這裡 一同敬拜讚美神",
        ]

        # Christian text corrections
        self.christian_corrections = [
            ("神", "上帝"),
            ("耶穌", "耶穌基督"),
            ("聖靈", "聖靈"),
            ("教会", "教會"),
            ("弟兄姊妹", "弟兄姊妹"),
            ("祷告", "禱告"),
            ("赞美", "讚美"),
            ("见证", "見證"),
            ("恩典", "恩典"),
            ("救恩", "救恩"),
        ]

        # Sample summaries
        self.christian_summaries = [
            "這段內容探討了基督教信仰的核心價值，包括愛、寬恕和救贖的重要性。作者強調透過禱告和讀經來建立與上帝的關係。",
            "講者分享了個人的信仰見證，描述了上帝在生活中的引導和恩典。內容涵蓋了如何在困難中持守信仰，以及聖靈的工作。",
            "這是一篇關於教會生活和弟兄姊妹團契的分享，強調了彼此相愛和互相扶持的重要性。內容包含了實際的屬靈操練建議。",
            "本段內容詳細闡述了基督教的救恩觀，解釋了耶穌基督的犧牲如何為人類帶來永生的盼望。作者呼籲聽眾回應福音。",
        ]

        self.general_summaries = [
            "本次討論主要聚焦於人工智慧技術的最新發展趋勢，包括機器學習演算法的改進以及在各行業的實際應用案例。",
            "演講者詳細介紹了深度學習在自然語言處理領域的突破性進展，特別強調了預訓練模型的重要性。",
            "此專案旨在開發先進的語音識別系统，結合最新的神經網路架構來提升識別準確度和處理效率。",
            "內容涵蓋了AI技術的基礎理論、實際應用場景，以及未來發展方向的深入分析。",
        ]

    async def transcribe_audio(
        self, _audio_chunk_path: str, language: str = "zh-TW", model: str = "mock-model"
    ) -> TranscriptionResult:
        selected_text = random.choice(self.sample_texts)

        # Create realistic timestamps
        words = selected_text.split()
        timestamps = []
        current_time = 0.0

        for _i, word in enumerate(words):
            word_duration = random.uniform(0.3, 0.8)  # Random word duration
            timestamps.append(
                {
                    "start": round(current_time, 1),
                    "end": round(current_time + word_duration, 1),
                    "text": word,
                }
            )
            current_time += word_duration + random.uniform(
                0.1, 0.3
            )  # Gap between words

        return TranscriptionResult(
            raw_text=selected_text,
            language=language,
            model=model,
        )

    async def correct_text(
        self, text: str, target_language: str = "zh-TW", model: str = "mock-model"
    ) -> CorrectionResult:
        # Apply Christian-specific corrections
        corrected = text
        for simplified, traditional in self.christian_corrections:
            corrected = corrected.replace(simplified, traditional)

        # Basic formatting improvements
        corrected = corrected.replace("  ", " ").strip()

        # Add proper punctuation if missing
        if corrected and not corrected.endswith(("。", "！", "？", "：", "；")):
            corrected += "。"

        return CorrectionResult(
            original_text=text,
            corrected_text=corrected,
            language=target_language,
            model=model,
        )

    async def summarize_text(
        self,
        text: str,  # noqa: ARG002
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "mock-model",
    ) -> SummaryResult:
        # Choose summary style based on model or instructions
        if "christian" in (instructions or "").lower() or "基督" in (
            instructions or ""
        ):
            summary = random.choice(self.christian_summaries)
        else:
            # Mix of both types for general use
            all_summaries = self.christian_summaries + self.general_summaries
            summary = random.choice(all_summaries)

        # Adjust length based on word limit - for Chinese, treat each character as a word
        if word_limit and len(summary) > word_limit:
            summary = summary[:word_limit] + "..."

        return SummaryResult(
            summary=summary,
            word_count=len(summary),
            model=model,
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
