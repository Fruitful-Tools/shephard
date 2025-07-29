"""Audio processing tasks for the pipeline."""

from pathlib import Path
from uuid import uuid4

from prefect import get_run_logger, task
from pydantic import HttpUrl
from pydub import AudioSegment

from shepherd_pipeline.services.youtube.schema import AudioResult

from ..services.llm_provider.schema import AudioChunk
from ..services.youtube.mock import MockYouTubeService
from ..services.youtube.service import YouTubeService
from ..utils.artifact_manager import ArtifactManager

# Import pydub for production audio processing
try:
    from pydub import AudioSegment  # type: ignore[import-untyped]
    from pydub.utils import make_chunks  # type: ignore[import-untyped]

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


@task(
    retries=3,
    retry_delay_seconds=[4, 8, 16],  # exponential backoff
    retry_jitter_factor=0.1,
)
async def download_youtube_audio(
    youtube_url: HttpUrl,
    start_time: float | None = None,
    end_time: float | None = None,
    use_mock: bool = False,
) -> AudioResult:
    """Download audio from YouTube URL with optional time range."""
    logger = get_run_logger()
    artifact_manager = ArtifactManager()
    audio_key = artifact_manager.get_artifact_key(
        url=str(youtube_url), start=start_time, end=end_time
    )

    # Check for existing download
    audio_result = artifact_manager.get_audio(audio_key)
    if audio_result:
        logger.info("Found existing download")
        return audio_result

    audio_folder = artifact_manager.audio_folder(audio_key)
    audio_folder.mkdir(parents=True, exist_ok=True)

    # Create output path in artifacts directory
    youtube_service: YouTubeService | MockYouTubeService = YouTubeService(
        root_dir=str(audio_folder)
    )
    if use_mock:
        # Use mock service
        youtube_service = MockYouTubeService(root_dir=str(audio_folder))
        artifact_manager.audio_folder(audio_key).mkdir(parents=True, exist_ok=True)

    result = await youtube_service.download_audio(
        str(youtube_url), start_time, end_time
    )
    artifact_manager.save_audio(audio_key, result)
    logger.info(f"Downloaded and saved audio to artifacts: {result.file_path}")
    return result


@task
async def chunk_audio(
    audio_result: AudioResult, chunk_size_minutes: int = 10, use_mock: bool = False
) -> list[AudioChunk]:
    """Split audio file into chunks for processing."""
    logger = get_run_logger()

    artifact_manager = ArtifactManager()
    chunks_dir = artifact_manager.chunk_folder(audio_result, chunk_size_minutes)
    chunks_dir.mkdir(parents=True, exist_ok=True)

    if use_mock:
        # Create mock chunks
        total_duration = 1800  # 30 minutes
        chunk_duration = chunk_size_minutes * 60

        chunks = []
        current_time = 0.0
        chunk_idx = 0

        while current_time < total_duration:
            end_time = min(current_time + chunk_duration, total_duration)
            chunk_path = str(chunks_dir / f"chunk_{uuid4()}_{chunk_idx}.mp3")

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

        logger.info(f"Created {len(chunks)} mock chunks")
        return chunks

    else:
        # Production audio chunking using pydub
        if not PYDUB_AVAILABLE:
            raise ImportError("pydub is required for production audio chunking")

        if not Path(audio_result.file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_result.file_path}")

        # Load audio file
        audio = AudioSegment.from_file(str(audio_result.file_path))

        # Convert chunk size from minutes to milliseconds
        chunk_duration_ms = chunk_size_minutes * 60 * 1000

        # Create chunks using pydub
        pydub_chunks = make_chunks(audio, chunk_duration_ms)

        chunks = []
        current_time = 0.0
        for i, chunk in enumerate(pydub_chunks):
            # Calculate timing based on actual accumulated duration
            start_time = current_time
            duration_seconds = len(chunk) / 1000.0  # pydub uses milliseconds
            end_time = start_time + duration_seconds
            current_time = end_time

            # Create chunk file path in artifacts directory
            chunk_path = str(chunks_dir / f"chunk_{uuid4()}_{i}.mp3")

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

        logger.info(f"Created {len(chunks)} chunks")
        return chunks
