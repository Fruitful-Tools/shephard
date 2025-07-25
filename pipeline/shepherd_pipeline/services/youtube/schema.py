"""YouTube service response schemas."""

from pydantic import BaseModel, Field


class AudioResult(BaseModel):
    """Response model for YouTube audio download."""

    title: str = Field(..., description="Video title")
    duration: float = Field(..., description="Actual audio duration in seconds")
    file_path: str = Field(..., description="Path to the downloaded audio file")
    format: str = Field(..., description="Audio format (e.g., mp3)")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: str | None = Field(
        None, description="Video upload date (YYYYMMDD format)"
    )
    original_duration: float = Field(
        ..., description="Original video duration in seconds"
    )
    start_time: float | None = Field(
        None, description="Start time if audio was clipped"
    )
    end_time: float | None = Field(None, description="End time if audio was clipped")
