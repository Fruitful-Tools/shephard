"""Mock Youtube API services for local development."""

from pathlib import Path
import random
import tempfile

from .schema import AudioResult


class MockYouTubeService:
    """Mock YouTube download service."""

    def __init__(self, root_dir: str | None = None) -> None:
        """Initialize mock YouTube service."""
        self.root_dir = root_dir or tempfile.gettempdir()

    async def download_audio(
        self,
        _url: str,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> AudioResult:
        """Mock YouTube audio download with optional time range."""

        # Mock video metadata
        original_duration = random.randint(300, 10800)  # 5 min to 3 hours

        # Calculate actual duration based on time range
        actual_duration: float = float(original_duration)
        if start_time is not None and end_time is not None:
            actual_duration = end_time - start_time
        elif start_time is not None:
            actual_duration = float(original_duration) - start_time
        elif end_time is not None:
            actual_duration = min(end_time, float(original_duration))

        # simple create mock file
        output_obj = Path(self.root_dir) / "audio.mp3"
        output_obj.parent.mkdir(parents=True, exist_ok=True)
        output_obj.touch()

        return AudioResult(
            title=f"Sample Video {random.randint(1000, 9999)}",
            duration=actual_duration,
            file_path=str(output_obj),
            format="mp3",
            sample_rate=44100,
            file_size=int(
                actual_duration * 128 * 1024 // 8
            ),  # Rough estimate for 128kbps
            upload_date="20240101",
            original_duration=original_duration,
            start_time=start_time,
            end_time=end_time,
        )
