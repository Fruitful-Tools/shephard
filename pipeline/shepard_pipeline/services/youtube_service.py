"""Real YouTube download service using yt-dlp."""

import asyncio
from pathlib import Path
import tempfile
from typing import Any

from loguru import logger
import yt_dlp  # type: ignore[import-untyped]


class YouTubeService:
    """Real YouTube download service using yt-dlp."""

    def __init__(self, temp_dir: str | None = None) -> None:
        """Initialize YouTube service.

        Args:
            temp_dir: Directory for temporary files. If None, uses system temp.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()

        # Loguru automatically handles logger configuration
        pass

    async def download_audio(
        self,
        url: str,
        output_path: str,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> dict[str, Any]:
        """Download audio from YouTube URL with optional time range.

        Args:
            url: YouTube video URL
            output_path: Output file path for the audio
            start_time: Start time in seconds (optional)
            end_time: End time in seconds (optional)

        Returns:
            Dictionary with video metadata and download info
        """
        output_path_obj = Path(output_path)
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

        # Add time range using download_sections if specified
        if start_time is not None or end_time is not None:
            sections = []
            if start_time is not None and end_time is not None:
                sections.append(f"*{start_time}-{end_time}")
            elif start_time is not None:
                sections.append(f"*{start_time}-inf")
            elif end_time is not None:
                sections.append(f"*0-{end_time}")

            if sections:
                ydl_opts["download_sections"] = sections

        try:
            # Run yt-dlp in a separate thread to avoid blocking
            info = await asyncio.to_thread(self._download_with_ytdl, url, ydl_opts)

            # Find the actual output file (yt-dlp may add its own extension)
            actual_output_path = self._find_output_file(output_path_obj)

            if not actual_output_path or not actual_output_path.exists():
                raise FileNotFoundError(f"Downloaded file not found at {output_path}")

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

            result = {
                "title": info.get("title", "Unknown Title"),
                "duration": actual_duration,
                "file_path": str(actual_output_path),
                "format": "mp3",
                "sample_rate": 44100,  # Default for mp3
                "file_size": file_size,
                "uploader": info.get("uploader", "Unknown"),
                "upload_date": info.get("upload_date"),
                "view_count": info.get("view_count"),
                "original_duration": info.get("duration", 0),
                "start_time": start_time,
                "end_time": end_time,
            }

            logger.success(
                f"Successfully downloaded: {result['title']} "
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

    async def get_video_info(self, url: str) -> dict[str, Any]:
        """Get video information without downloading.

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video metadata
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }

        try:
            info = await asyncio.to_thread(self._extract_info, url, ydl_opts)

            return {
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "upload_date": info.get("upload_date"),
                "view_count": info.get("view_count"),
                "description": info.get("description", ""),
                "thumbnail": info.get("thumbnail"),
                "formats": [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "quality": f.get("quality"),
                    }
                    for f in info.get("formats", [])
                    if f.get("vcodec") == "none"  # Audio only
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get video info for {url}: {e}")
            raise

    def _extract_info(self, url: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
        """Extract video info using yt-dlp (blocking operation)."""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: dict[str, Any] = ydl.extract_info(url, download=False)
            return info
