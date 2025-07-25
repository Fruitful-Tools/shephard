"""Audio processing tasks."""

from pathlib import Path
from typing import Any
from uuid import uuid4

from prefect import task
from pydantic import HttpUrl

from ..config.settings import settings
from ..models.pipeline import AudioChunk
from ..services.mock_apis import MockYouTubeService
from ..services.youtube_service import YouTubeService

# Import pydub for production audio processing
try:
    from pydub import AudioSegment  # type: ignore[import-untyped]
    from pydub.utils import make_chunks  # type: ignore[import-untyped]

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


@task(retries=2, retry_delay_seconds=5)
async def download_youtube_audio(
    youtube_url: HttpUrl,
    output_dir: str,
    start_time: float | None = None,
    end_time: float | None = None,
) -> dict[str, Any]:
    """Download audio from YouTube URL with optional time range."""
    # Create output path
    output_path = Path(output_dir) / f"youtube_audio_{uuid4()}.mp3"

    if settings.mock_external_apis:
        # Use mock service
        mock_service = MockYouTubeService()
        result = await mock_service.download_audio(
            str(youtube_url), str(output_path), start_time, end_time
        )

        # Create a mock audio file for chunking
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()

        return result
    else:
        # Use real YouTube service
        real_service = YouTubeService(temp_dir=output_dir)
        return await real_service.download_audio(
            str(youtube_url), str(output_path), start_time, end_time
        )


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

    if settings.mock_external_apis:
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
        # Production audio chunking using pydub
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub is required for production audio chunking")

        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Load audio file
        audio = AudioSegment.from_file(str(audio_path))

        # Convert chunk size from minutes to milliseconds
        chunk_duration_ms = chunk_size_minutes * 60 * 1000

        # Create chunks using pydub
        pydub_chunks = make_chunks(audio, chunk_duration_ms)

        chunks = []
        for i, chunk in enumerate(pydub_chunks):
            # Calculate timing
            start_time = i * chunk_size_minutes * 60
            duration_seconds = len(chunk) / 1000.0  # pydub uses milliseconds
            end_time = start_time + duration_seconds

            # Create chunk file path
            chunk_path = f"{audio_file_path}_chunk_{i}.mp3"

            # Export chunk to file
            chunk.export(chunk_path, format="mp3")

            chunks.append(
                AudioChunk(
                    chunk_id=f"chunk_{i}",
                    start_time=start_time,
                    end_time=end_time,
                    file_path=chunk_path,
                    duration=duration_seconds,
                )
            )

        return chunks


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
