"""Command-line interface for Shepard Pipeline."""

import asyncio

from rich.console import Console
from rich.table import Table
import typer

from ..flows.main_flows import (
    run_audio_pipeline,
    run_text_pipeline,
    run_youtube_pipeline,
)
from ..models.pipeline import JobStatus, PipelineResult

app = typer.Typer(help="Shepard Pipeline CLI")
console = Console()


@app.command()
def youtube(
    url: str = typer.Argument(..., help="YouTube URL to process"),
    user_id: str | None = typer.Option(None, "--user", help="User ID"),
    language: str = typer.Option("zh-TW", "--lang", help="Target language"),
    chunk_size: int = typer.Option(10, "--chunk-size", help="Chunk size in minutes"),
    summary_limit: int | None = typer.Option(
        None, "--summary-limit", help="Summary word limit"
    ),
    instructions: str | None = typer.Option(
        None, "--instructions", help="Custom instructions"
    ),
) -> None:
    """Process YouTube video through the pipeline."""
    console.print(f"[blue]Starting YouTube pipeline for: {url}[/blue]")

    async def run() -> None:
        result = await run_youtube_pipeline(
            youtube_url=url,
            user_id=user_id,
            target_language=language,
            chunk_size_minutes=chunk_size,
            summary_word_limit=summary_limit,
            summary_instructions=instructions,
        )

        display_result(result)

    asyncio.run(run())


@app.command()
def audio(
    file_path: str = typer.Argument(..., help="Path to audio file"),
    user_id: str | None = typer.Option(None, "--user", help="User ID"),
    language: str = typer.Option("zh-TW", "--lang", help="Target language"),
    chunk_size: int = typer.Option(10, "--chunk-size", help="Chunk size in minutes"),
    summary_limit: int | None = typer.Option(
        None, "--summary-limit", help="Summary word limit"
    ),
    instructions: str | None = typer.Option(
        None, "--instructions", help="Custom instructions"
    ),
) -> None:
    """Process audio file through the pipeline."""
    console.print(f"[blue]Starting audio pipeline for: {file_path}[/blue]")

    async def run() -> None:
        result = await run_audio_pipeline(
            audio_file_path=file_path,
            user_id=user_id,
            target_language=language,
            chunk_size_minutes=chunk_size,
            summary_word_limit=summary_limit,
            summary_instructions=instructions,
        )

        display_result(result)

    asyncio.run(run())


@app.command()
def text(
    content: str = typer.Argument(..., help="Text content to summarize"),
    user_id: str | None = typer.Option(None, "--user", help="User ID"),
    language: str = typer.Option("zh-TW", "--lang", help="Target language"),
    summary_limit: int | None = typer.Option(
        None, "--summary-limit", help="Summary word limit"
    ),
    instructions: str | None = typer.Option(
        None, "--instructions", help="Custom instructions"
    ),
) -> None:
    """Process text through summarization pipeline."""
    console.print("[blue]Starting text summarization pipeline[/blue]")

    async def run() -> None:
        result = await run_text_pipeline(
            text_content=content,
            user_id=user_id,
            target_language=language,
            summary_word_limit=summary_limit,
            summary_instructions=instructions,
        )

        display_result(result)

    asyncio.run(run())


def display_result(result: PipelineResult) -> None:
    """Display pipeline result in a formatted table."""

    # Create summary table
    table = Table(title=f"Pipeline Result - Job {result.job_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row(
        "Status",
        f"[green]{result.status}[/green]"
        if result.status == JobStatus.COMPLETED
        else f"[red]{result.status}[/red]",
    )
    table.add_row("Entry Point", result.entry_point.value)
    table.add_row("Credits Consumed", str(result.credits_consumed))

    if result.completed_at and result.started_at:
        duration = (result.completed_at - result.started_at).total_seconds()
        table.add_row("Duration", f"{duration:.1f} seconds")

    if result.audio_chunks:
        table.add_row("Audio Chunks", str(len(result.audio_chunks)))

    if result.transcriptions:
        table.add_row("Transcriptions", str(len(result.transcriptions)))

    if result.error_message:
        table.add_row("Error", f"[red]{result.error_message}[/red]")

    console.print(table)

    # Display summary if available
    if result.summary:
        console.print("\n[green]Summary:[/green]")
        console.print(f"[dim]Word Count: {result.summary.word_count}[/dim]")
        console.print(f"[dim]Model: {result.summary.model_used}[/dim]")
        console.print()
        console.print(result.summary.summary)

    # Display transcriptions if available (truncated)
    if result.transcriptions:
        console.print("\n[blue]Transcriptions (sample):[/blue]")
        for i, trans in enumerate(result.transcriptions[:3]):  # Show first 3
            console.print(f"[dim]Chunk {i + 1}:[/dim] {trans.raw_text[:100]}...")

        if len(result.transcriptions) > 3:
            console.print(
                f"[dim]... and {len(result.transcriptions) - 3} more chunks[/dim]"
            )


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
