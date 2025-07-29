"""Summarization-related Prefect tasks."""

from prefect import task

from ..services.llm_provider.schema import SummaryResult
from ..services.model_factory import ModelFactory


@task(
    retries=3,
    retry_delay_seconds=[4, 8, 16],  # exponential backoff
    retry_jitter_factor=0.1,
)
async def summarize_text(
    text: str,
    instructions: str | None = None,
    word_limit: int | None = None,
    model: str = "mistral-small-latest",
) -> SummaryResult:
    """Generate summary from the merged text using Mistral API."""

    # Use model factory to create appropriate service
    summarizer = ModelFactory.create_summarization_service(model=model)

    # All services now use consistent interface
    result = await summarizer.summarize_text(
        text=text, instructions=instructions, word_limit=word_limit, model=model
    )
    if result.failure_reason:
        raise RuntimeError(
            f"Summarization failed for {text[:100]}: {result.failure_reason}"
        )
    return result


@task
async def validate_summary_quality(summary: SummaryResult, original_text: str) -> bool:
    """Validate summary quality and completeness."""

    # Basic validation checks
    if not summary.summary or len(summary.summary.strip()) < 10:
        return False

    # Check if summary is not just a copy of original
    if summary.summary.strip() == original_text.strip():
        return False

    # Check word count matches reported count
    actual_word_count = len(summary.summary.split())
    return abs(actual_word_count - summary.word_count) <= 5
