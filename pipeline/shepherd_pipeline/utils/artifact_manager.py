"""Artifact management for pipeline intermediate results."""

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any, TypeVar

from pydantic import BaseModel

from shepherd_pipeline.services.youtube.schema import AudioResult

T = TypeVar("T", bound=BaseModel)

ARTIFACTS_DIR = Path("pipeline_artifacts")


@dataclass
class PipelineState:
    """Pipeline execution state for resume capability."""

    job_id: str
    completed_stages: list[str]
    failed_stages: list[str]
    stage_metadata: dict[str, dict[str, Any]]
    partial_completions: dict[str, list[str]]
    last_updated: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "stage_metadata": self.stage_metadata,
            "partial_completions": self.partial_completions,
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PipelineState":
        return cls(
            job_id=data["job_id"],
            completed_stages=data["completed_stages"],
            failed_stages=data["failed_stages"],
            stage_metadata=data["stage_metadata"],
            partial_completions=data["partial_completions"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )


class ArtifactManager:
    """Manages storage and retrieval of pipeline artifacts."""

    def __init__(self) -> None:
        """Initialize artifact manager."""
        # Ensure legacy directories exist
        (ARTIFACTS_DIR / "downloads").mkdir(parents=True, exist_ok=True)

        # Ensure new directory structure exists
        (ARTIFACTS_DIR / "jobs").mkdir(parents=True, exist_ok=True)

    def get_artifact_key(self, **kwargs: str | float | int | None) -> str:
        """Generate artifact key from parameters."""
        # Create deterministic hash from parameters
        content = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def audio_folder(self, key: str) -> Path:
        """Get the path to the youtube audio file."""
        return ARTIFACTS_DIR / "downloads" / key

    def get_audio(self, key: str) -> AudioResult | None:
        """Check if the youtube audio exists in the artifacts directory."""
        metadata_path = self.audio_folder(key) / "metadata.json"
        if not metadata_path.exists():
            return None
        metadata = AudioResult.model_validate_json(metadata_path.read_text())
        return metadata

    def save_audio(self, key: str, audio_result: AudioResult) -> None:
        """Save the youtube audio file."""
        metadata_path = self.audio_folder(key) / "metadata.json"
        metadata_path.write_text(audio_result.model_dump_json())

    def chunk_folder(self, audio_result: AudioResult, chunk_size_minutes: int) -> Path:
        audio_key = audio_result.file_path.split("/")[-1].split(".")[0]
        return ARTIFACTS_DIR / "chunks" / f"{chunk_size_minutes}min" / audio_key

    def remove_chunks(self, audio_result: AudioResult, chunk_size_minutes: int) -> None:
        """Remove the chunks for a given audio result."""
        chunk_folder = self.chunk_folder(audio_result, chunk_size_minutes)
        if chunk_folder.exists():
            shutil.rmtree(chunk_folder)
