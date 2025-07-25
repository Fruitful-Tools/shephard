"""Real YouTube download service using yt-dlp."""

import asyncio
from pathlib import Path
import tempfile
from typing import Any

from loguru import logger
import yt_dlp  # type: ignore[import-untyped]

from .schema import AudioResult


class YouTubeService:
    """Real YouTube download service using yt-dlp."""

    def __init__(self, root_dir: str | None = None) -> None:
        """Initialize YouTube service.

        Args:
            temp_dir: Directory for temporary files. If None, uses system temp.
        """
        self.root_dir = root_dir or tempfile.gettempdir()

        # Loguru automatically handles logger configuration
        pass

    async def download_audio(
        self,
        url: str,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> AudioResult:
        """Download audio from YouTube URL with optional time range.

        Args:
            url: YouTube video URL
            output_path: Output file path for the audio
            start_time: Start time in seconds (optional)
            end_time: End time in seconds (optional)

        Returns:
            AudioResult with video metadata and download info
        """
        output_path_obj = Path(self.root_dir) / "audio.mp3"
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Configure yt-dlp options
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": str(
                output_path_obj.with_suffix("")
            ),  # yt-dlp will add extension
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        # Add postprocessor for audio conversion
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]

        # Add time range using FFmpeg postprocessor if specified
        if start_time is not None or end_time is not None:
            ffmpeg_options = []
            if start_time is not None:
                ffmpeg_options.extend(["-ss", str(start_time)])
            if end_time is not None:
                duration = end_time - (start_time or 0)
                ffmpeg_options.extend(["-t", str(duration)])

            # Add FFmpeg postprocessor with time options
            if ffmpeg_options:
                ydl_opts["postprocessor_args"] = {"ffmpeg": ffmpeg_options}

        try:
            # Run yt-dlp in a separate thread to avoid blocking
            info = await asyncio.to_thread(self._download_with_ytdl, url, ydl_opts)

            # Find the actual output file (yt-dlp may add its own extension)
            actual_output_path = self._find_output_file(output_path_obj)

            if not actual_output_path or not actual_output_path.exists():
                raise FileNotFoundError(
                    f"Downloaded file not found at {output_path_obj}"
                )

            # Get file size
            file_size = actual_output_path.stat().st_size

            # Calculate actual duration if time range was specified
            actual_duration = info.get("duration", 0)
            if start_time is not None and end_time is not None:
                actual_duration = end_time - start_time
            elif start_time is not None:
                actual_duration = actual_duration - start_time
            elif end_time is not None:
                actual_duration = min(end_time, actual_duration)

            result = AudioResult(
                title=info.get("title", "Unknown Title"),
                duration=actual_duration,
                file_path=str(actual_output_path),
                format="mp3",
                sample_rate=44100,  # Default for mp3
                file_size=file_size,
                upload_date=info.get("upload_date"),
                original_duration=info.get("duration", 0),
                start_time=start_time,
                end_time=end_time,
            )

            logger.success(
                f"Successfully downloaded: {result.title} "
                f"({actual_duration:.1f}s, {file_size / 1024 / 1024:.1f}MB)"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to download YouTube video {url}: {e}")
            raise

    def _download_with_ytdl(self, url: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
        """Download video using yt-dlp (blocking operation)."""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info: dict[str, Any] = ydl.extract_info(url, download=False)

            # Then download
            ydl.download([url])

            return info

    def _find_output_file(self, expected_path: Path) -> Path | None:
        """Find the actual output file created by yt-dlp."""
        # yt-dlp might create files with different extensions
        possible_extensions = [".mp3", ".m4a", ".webm", ".ogg"]
        base_path = expected_path.with_suffix("")

        for ext in possible_extensions:
            candidate = base_path.with_suffix(ext)
            if candidate.exists():
                return candidate

        # Also check if the exact path exists
        if expected_path.exists():
            return expected_path

        return None
