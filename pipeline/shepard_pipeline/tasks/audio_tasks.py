"""Audio processing tasks."""

from pathlib import Path
from typing import Any
from uuid import uuid4

from prefect import task
from pydantic import HttpUrl

from ..config.settings import settings
from ..models.pipeline import AudioChunk
from ..services.mock_apis import MockYouTubeService


@task(retries=2, retry_delay_seconds=5)
async def download_youtube_audio(
    youtube_url: HttpUrl, output_dir: str
) -> dict[str, Any]:
    """Download audio from YouTube URL."""
    youtube_service = MockYouTubeService()

    # Create output path
    output_path = Path(output_dir) / f"youtube_audio_{uuid4()}.mp3"

    if settings.is_development:
        result = await youtube_service.download_audio(
            str(youtube_url), str(output_path)
        )

        # Create a mock audio file for chunking
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()

        return result
    else:
        # TODO: Implement real YouTube download using yt-dlp
        raise NotImplementedError("Production YouTube download not implemented")


@task
async def validate_audio_file(file_path: str) -> dict[str, Any]:
    """Validate audio file and extract metadata."""
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # Mock audio metadata
    file_size = file_path_obj.stat().st_size if file_path_obj.exists() else 1024000

    return {
        "file_path": file_path,
        "duration": 1800,  # 30 minutes mock
        "format": "mp3",
        "sample_rate": 44100,
        "file_size": file_size,
        "channels": 2,
    }


@task
async def chunk_audio(
    audio_file_path: str, chunk_size_minutes: int = 10
) -> list[AudioChunk]:
    """Split audio file into chunks for processing."""

    # Mock chunking - in reality would use pydub or ffmpeg
    if settings.is_development:
        # Create mock chunks
        total_duration = 1800  # 30 minutes
        chunk_duration = chunk_size_minutes * 60

        chunks = []
        current_time = 0.0
        chunk_idx = 0

        while current_time < total_duration:
            end_time = min(current_time + chunk_duration, total_duration)

            chunk_path = f"{audio_file_path}_chunk_{chunk_idx}.mp3"

            # Create mock chunk file
            Path(chunk_path).touch()

            chunks.append(
                AudioChunk(
                    chunk_id=f"chunk_{chunk_idx}",
                    start_time=current_time,
                    end_time=end_time,
                    file_path=chunk_path,
                    duration=end_time - current_time,
                )
            )

            current_time = end_time
            chunk_idx += 1

        return chunks

    else:
        # TODO: Implement real audio chunking using pydub
        raise NotImplementedError("Production audio chunking not implemented")


@task
async def cleanup_temp_files(file_paths: list[str]) -> None:
    """Clean up temporary audio files."""
    for file_path in file_paths:
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_path_obj.unlink()
        except Exception as e:
            print(f"Warning: Could not remove {file_path}: {e}")
