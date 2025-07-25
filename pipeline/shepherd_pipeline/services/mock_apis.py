"""Mock external API services for local development."""

import random
import time
from typing import Any
from uuid import uuid4


class MockSupabaseService:
    """Mock Supabase database service."""

    def __init__(self) -> None:
        self.jobs_db: dict[str, dict[str, Any]] = {}  # In-memory job storage

    async def create_job_record(self, job_data: dict[str, Any]) -> str:
        """Create a new job record."""
        job_id = str(uuid4())
        self.jobs_db[job_id] = {
            **job_data,
            "id": job_id,
            "created_at": time.time(),
            "status": "pending",
        }
        return job_id

    async def update_job_status(self, job_id: str, status: str, **kwargs: Any) -> None:  # noqa: ANN401
        """Update job status and metadata."""
        if job_id in self.jobs_db:
            self.jobs_db[job_id].update(
                {"status": status, "updated_at": time.time(), **kwargs}
            )

    async def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Get job by ID."""
        return self.jobs_db.get(job_id)

    async def check_user_quota(self, _user_id: str) -> dict[str, int]:
        """Check user's remaining quota and credits."""
        return {
            "daily_quota_remaining": random.randint(0, 5),
            "credits_remaining": random.randint(1, 50),
            "total_jobs_today": random.randint(0, 3),
        }
