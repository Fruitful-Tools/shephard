"""Text summarization tasks."""

from prefect import task

from ..config.settings import settings
from ..models.pipeline import SummaryResult
from ..services.mock_apis import MockOpenAIService


@task(retries=2, retry_delay_seconds=10)
async def summarize_text(
    text: str,
    instructions: str | None = None,
    word_limit: int | None = None,
    model: str = "gpt-4",
) -> SummaryResult:
    """Generate summary from the merged text."""

    if settings.is_development:
        openai_service = MockOpenAIService()
        return await openai_service.summarize_text(
            _text=text, instructions=instructions, word_limit=word_limit, model=model
        )
    else:
        # TODO: Implement real OpenAI API call
        raise NotImplementedError("Production summarization not implemented")


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
