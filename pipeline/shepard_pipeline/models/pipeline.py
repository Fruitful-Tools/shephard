"""Pipeline data models and schemas."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, model_validator


class JobStatus(str, Enum):
    """Pipeline job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EntryPointType(str, Enum):
    """Pipeline entry point types."""

    YOUTUBE = "youtube"
    AUDIO_FILE = "audio_file"
    TEXT = "text"


class AudioChunk(BaseModel):
    """Audio chunk data."""

    chunk_id: str
    start_time: float
    end_time: float
    file_path: str
    duration: float


class TranscriptionResult(BaseModel):
    """Transcription result for a single chunk."""

    chunk_id: str
    raw_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    language: str
    timestamps: list[dict[str, Any]] = Field(default_factory=list)


class CorrectionResult(BaseModel):
    """Text correction/translation result."""

    chunk_id: str
    original_text: str
    corrected_text: str
    language: str
    model_used: str


class SummaryResult(BaseModel):
    """Final summary result."""

    summary: str
    word_count: int
    model_used: str
    custom_instructions: str | None = None


class PipelineInput(BaseModel):
    """Input parameters for pipeline execution."""

    entry_point: EntryPointType

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

    @model_validator(mode="after")
    def validate_entry_point_data(self) -> "PipelineInput":
        """Validate that appropriate data is provided for entry point."""
        if self.entry_point == EntryPointType.YOUTUBE and not self.youtube_url:
            raise ValueError("youtube_url is required for YOUTUBE entry point")
        elif self.entry_point == EntryPointType.AUDIO_FILE and not self.audio_file_path:
            raise ValueError("audio_file_path is required for AUDIO_FILE entry point")
        elif self.entry_point == EntryPointType.TEXT and not self.text_content:
            raise ValueError("text_content is required for TEXT entry point")

        # Validate YouTube time parameters
        if (
            self.youtube_start_time is not None
            and self.youtube_end_time is not None
            and self.youtube_end_time <= self.youtube_start_time
        ):
            raise ValueError("youtube_end_time must be greater than youtube_start_time")

        return self


class PipelineResult(BaseModel):
    """Complete pipeline execution result."""

    job_id: UUID
    user_id: str | None = None
    status: JobStatus
    entry_point: EntryPointType

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


class JobSubmissionResponse(BaseModel):
    """Response for job submission."""

    job_id: UUID
    status: JobStatus
    message: str
    estimated_credits: int
    estimated_duration_minutes: float | None = None
