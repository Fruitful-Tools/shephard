"""Pipeline data models and schemas."""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from ..services.llm_provider.schema import (
    AudioChunk,
    CorrectionResult,
    SummaryResult,
    TranscriptionResult,
)


class JobStatus(str, Enum):
    """Pipeline job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineInput(BaseModel):
    """Input parameters for pipeline execution."""

    # Source data (one of these will be provided)
    youtube_url: HttpUrl | None = None
    audio_file_path: str | None = None
    text_content: str | None = None

    # YouTube-specific parameters
    youtube_start_time: float | None = Field(
        default=None, ge=0, description="Start time in seconds for YouTube videos"
    )
    youtube_end_time: float | None = Field(
        default=None, ge=0, description="End time in seconds for YouTube videos"
    )

    # Processing parameters
    chunk_size_minutes: int = Field(default=10, ge=1, le=30)
    target_language: str = Field(default="zh-TW")

    # Model selection
    transcription_model: str = Field(default="voxtral-v1")
    correction_model: str = Field(default="mistral-medium")
    summarization_model: str = Field(default="gpt-4")

    # Summarization parameters
    summary_instructions: str | None = None
    summary_word_limit: int | None = Field(default=None, ge=50, le=2000)

    # User context
    user_id: str | None = None
    job_id: UUID | None = Field(default_factory=uuid4)


class PipelineResult(BaseModel):
    """Complete pipeline execution result."""

    job_id: UUID | None = None
    user_id: str | None = None
    status: JobStatus

    # Processing results
    audio_chunks: list[AudioChunk] = Field(default_factory=list)
    transcriptions: list[TranscriptionResult] = Field(default_factory=list)
    corrections: list[CorrectionResult] = Field(default_factory=list)
    summary: SummaryResult | None = None

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    # Resource usage
    credits_consumed: int = 0
    processing_duration: float | None = None  # seconds

    # Input parameters (for reference)
    input_params: PipelineInput | None = None

    @property
    def is_complete(self) -> bool:
        """Check if pipeline is complete."""
        return self.status in [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        ]

    @property
    def duration_minutes(self) -> float | None:
        """Get processing duration in minutes."""
        if self.processing_duration:
            return self.processing_duration / 60.0
        return None
