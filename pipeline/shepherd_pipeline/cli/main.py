"""Command-line interface for Shepherd Pipeline."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Annotated

from pydantic import HttpUrl
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import typer

from ..flows.main_flows import youtube_pipeline_flow
from ..models.pipeline import JobStatus, PipelineInput, PipelineResult
from ..services.model_factory import AIProvider, ModelFactory, TaskType

app = typer.Typer(
    help="Shepherd Pipeline CLI - AI-powered transcription and summarization"
)
console = Console()


def resolve_model_and_provider(
    provider: str | None, model: str | None, task_type: TaskType
) -> tuple[AIProvider, str]:
    """Resolve model and provider with validation and defaults."""
    # If no model provided, use default for provider
    if model is None:
        ai_provider = AIProvider(provider) if provider else AIProvider.MISTRAL
        default_model = ModelFactory.get_default_model_for_provider(
            ai_provider, task_type
        )
        return ai_provider, default_model

    # If model provided but no provider, infer provider from model
    if provider is None:
        ai_provider = ModelFactory.get_provider_for_model(model)
        if not ModelFactory.validate_model(ai_provider, model, task_type):
            console.print(
                f"[yellow]Model '{model}' not supported for {task_type.value}. Using default.[/yellow]"
            )
            default_model = ModelFactory.get_default_model_for_provider(
                ai_provider, task_type
            )
            return ai_provider, default_model
        return ai_provider, model

    # Both provided - validate compatibility
    try:
        ai_provider = AIProvider(provider)
    except ValueError:
        console.print(
            f"[red]Unknown provider: {provider}. Using mistral instead.[/red]"
        )
        ai_provider = AIProvider.MISTRAL

    # Validate model supports task type and provider
    if not ModelFactory.validate_model(ai_provider, model, task_type):
        default_model = ModelFactory.get_default_model_for_provider(
            ai_provider, task_type
        )
        console.print(
            f"[yellow]Model '{model}' not compatible with {provider}/{task_type.value}. Using '{default_model}'.[/yellow]"
        )
        return ai_provider, default_model

    return ai_provider, model


def save_transcript_and_summary(
    result: PipelineResult,
    transcript_path: str | None = None,
    summary_path: str | None = None,
) -> None:
    """Save the full transcript and summary to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Prepare default paths if not provided
    if transcript_path:
        transcript_path = transcript_path.replace("{timestamp}", timestamp)
    if summary_path:
        summary_path = summary_path.replace("{timestamp}", timestamp)

    # Save full transcript if corrections are available
    if transcript_path and result.corrections:
        try:
            # Create parent directory if it doesn't exist
            Path(transcript_path).parent.mkdir(parents=True, exist_ok=True)

            # Combine all corrected texts to create full transcript
            full_transcript = "\n".join(
                [
                    f"{correction.corrected_text}"
                    for i, correction in enumerate(result.corrections)
                ]
            )

            # Write transcript to file
            Path(transcript_path).write_text(full_transcript, encoding="utf-8")
            console.print(
                f"✅ Full transcript saved to: {Path(transcript_path).absolute()}"
            )
            console.print(f"   Total length: {len(full_transcript)} characters")

        except Exception as e:
            console.print(f"❌ Error saving transcript: {e}")

    # Save summary if available
    if summary_path and result.summary:
        try:
            # Create parent directory if it doesn't exist
            Path(summary_path).parent.mkdir(parents=True, exist_ok=True)

            # Create detailed summary with metadata
            summary_content = f"""# Pipeline Summary Report

## Processing Information
- Status: {result.status.value}
- Job ID: {result.job_id}
- User ID: {result.user_id or "N/A"}
- Processing Duration: {f"{result.processing_duration:.1f}s" if result.processing_duration else "N/A"}

## Content Information
- URL: {result.input_params.youtube_url if result.input_params and result.input_params.youtube_url else "N/A"}
- Duration processed: {result.input_params.youtube_end_time - result.input_params.youtube_start_time if result.input_params and result.input_params.youtube_start_time and result.input_params.youtube_end_time else "N/A"} seconds
- Language: {result.input_params.target_language if result.input_params else "N/A"}
- Model used: {result.summary.model}
- Word count: {result.summary.word_count}
- Character count: {len(result.summary.summary)}

## Summary

{result.summary.summary}

## Processing Details
- Audio chunks: {len(result.audio_chunks)}
- Transcriptions: {len(result.transcriptions)}
- Corrections: {len(result.corrections)}
- Credits consumed: {result.credits_consumed}
- Timestamp: {timestamp}
"""

            # Write summary to file
            Path(summary_path).write_text(summary_content, encoding="utf-8")
            console.print(f"✅ Summary saved to: {Path(summary_path).absolute()}")
            console.print(
                f"   Summary length: {len(result.summary.summary)} characters"
            )

        except Exception as e:
            console.print(f"❌ Error saving summary: {e}")


@app.command()
def youtube(
    url: Annotated[str, typer.Argument(help="YouTube URL to process")],
    export_transcript: Annotated[
        str | None,
        typer.Option(
            "--export-transcript",
            help="Export transcript to file (use {timestamp} for timestamp)",
        ),
    ] = None,
    export_summary: Annotated[
        str | None,
        typer.Option(
            "--export-summary",
            help="Export summary to file (use {timestamp} for timestamp)",
        ),
    ] = None,
    transcribe_provider: Annotated[
        str | None,
        typer.Option(
            "--transcription-provider", help="Transcription provider (mistral/openai)"
        ),
    ] = None,
    transcribe_model: Annotated[
        str | None,
        typer.Option("--transcription-model", help="Transcription model name"),
    ] = None,
    correction_provider: Annotated[
        str | None,
        typer.Option(
            "--correction-provider", help="Correction provider (mistral/openai)"
        ),
    ] = None,
    correction_model: Annotated[
        str | None, typer.Option("--correction-model", help="Correction model name")
    ] = None,
    summary_provider: Annotated[
        str | None,
        typer.Option("--summary-provider", help="Summary provider (mistral/openai)"),
    ] = None,
    summary_model: Annotated[
        str | None, typer.Option("--summary-model", help="Summary model name")
    ] = None,
    mock: Annotated[
        bool,
        typer.Option("--mock/--no-mock", help="Use mock APIs instead of real ones"),
    ] = False,
    audio_chunk_interval: Annotated[
        int,
        typer.Option("--audio-chunk-interval", help="Audio chunk interval in minutes"),
    ] = 10,
    summary_word_count: Annotated[
        int, typer.Option("--summary-word-count", help="Target word count for summary")
    ] = 1500,
    start: Annotated[
        float | None, typer.Option("--start", help="Start time in seconds")
    ] = None,
    end: Annotated[
        float | None, typer.Option("--end", help="End time in seconds")
    ] = None,
    summary_instruction: Annotated[
        str | None,
        typer.Option("--summary-instruction", help="Custom summary instructions"),
    ] = None,
    user_id: Annotated[str | None, typer.Option("--user", help="User ID")] = None,
    language: Annotated[str, typer.Option("--lang", help="Target language")] = "zh-TW",
) -> None:
    """Process YouTube video through the pipeline."""
    # Configure mock mode
    if mock:
        console.print(
            "[yellow]Running in MOCK mode - no external API calls will be made[/yellow]"
        )

    # Resolve models and providers
    if not mock:
        _, transcribe_model_resolved = resolve_model_and_provider(
            transcribe_provider, transcribe_model, TaskType.TRANSCRIPTION
        )
        _, correction_model_resolved = resolve_model_and_provider(
            correction_provider, correction_model, TaskType.CORRECTION
        )
        _, summary_model_resolved = resolve_model_and_provider(
            summary_provider, summary_model, TaskType.SUMMARIZATION
        )
    else:
        transcribe_model_resolved = "mock-model"
        correction_model_resolved = "mock-model"
        summary_model_resolved = "mock-model"

    console.print(
        Panel(
            f"[bold blue]YouTube Pipeline[/bold blue]\n"
            f"URL: {url}\n"
            f"Time Range: {f'{start}s - {end}s' if start and end else 'Full video'}\n"
            f"Mock: {mock}\n"
            f"Mode: {'Mock' if mock else 'Real APIs'}\n"
            f"Transcription Model: {transcribe_model_resolved}\n"
            f"Correction Model: {correction_model_resolved}\n"
            f"Summary Model: {summary_model_resolved}",
            title="🎥 Processing YouTube Video",
        )
    )

    # Set default export paths if not provided but requested
    if export_transcript is None:
        export_transcript = "exports/transcript-{timestamp}.txt"
    if export_summary is None:
        export_summary = "exports/summary-{timestamp}.txt"

    async def run() -> None:
        pipeline_input = PipelineInput(
            youtube_url=HttpUrl(url),
            youtube_start_time=start,
            youtube_end_time=end,
            user_id=user_id,
            target_language=language,
            chunk_size_minutes=audio_chunk_interval,
            transcription_model=transcribe_model_resolved,
            correction_model=correction_model_resolved,
            summarization_model=summary_model_resolved,
            summary_instructions=summary_instruction,
            summary_word_limit=summary_word_count,
        )
        result = await youtube_pipeline_flow(
            pipeline_input=pipeline_input,
            use_mock=mock,
        )

        display_result(result)

        # Save files if requested
        console.print(result.corrections)
        if export_transcript or export_summary:
            console.print("\n📁 Exporting results...")
            save_transcript_and_summary(result, export_transcript, export_summary)

    asyncio.run(run())


@app.command()
def models() -> None:
    """List all available models grouped by provider."""
    console.print(
        Panel(
            "[bold magenta]Available Models[/bold magenta]",
            title="🤖 Model Configuration",
        )
    )

    supported_models = ModelFactory.get_supported_models()

    for provider, models in supported_models.items():
        if models:  # Only show providers with models
            table = Table(title=f"{provider.value.upper()} Models")
            table.add_column("Model Name", style="cyan")
            table.add_column("Supported Tasks", style="green")

            for model in sorted(models):
                # Get tasks from model configuration
                config = ModelFactory.MODEL_CONFIG.get(model, {})
                supported_tasks = config.get("tasks", [])

                # Format task names nicely
                task_names = []
                for task in supported_tasks:
                    if task == TaskType.TRANSCRIPTION:
                        task_names.append("Transcription")
                    elif task == TaskType.CORRECTION:
                        task_names.append("Correction")
                    elif task == TaskType.SUMMARIZATION:
                        task_names.append("Summarization")

                tasks = ", ".join(task_names) if task_names else "Unknown"
                table.add_row(model, tasks)

            console.print(table)
            console.print()


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
    table.add_row("Credits Consumed", str(result.credits_consumed))

    if result.completed_at and result.started_at:
        duration = (result.completed_at - result.started_at).total_seconds()
        table.add_row("Duration", f"{duration:.1f} seconds")

    if result.audio_chunks:
        table.add_row("Audio Chunks", str(len(result.audio_chunks)))

    if result.transcriptions:
        table.add_row("Transcriptions", str(len(result.transcriptions)))

    if result.corrections:
        table.add_row("Corrections", str(len(result.corrections)))

    if result.error_message:
        table.add_row("Error", f"[red]{result.error_message}[/red]")

    console.print(table)

    # Display summary if available
    if result.summary:
        console.print("\n[green]Summary:[/green]")
        console.print(f"[dim]Word Count: {result.summary.word_count}[/dim]")
        console.print(f"[dim]Character Count: {len(result.summary.summary)}[/dim]")
        console.print(f"[dim]Model: {result.summary.model}[/dim]")
        console.print()
        console.print(
            Panel(
                result.summary.summary,
                title="📋 Generated Summary",
                border_style="green",
            )
        )

    # Display sample transcriptions if available
    if result.transcriptions and len(result.transcriptions) > 0:
        console.print("\n[blue]Sample Transcriptions:[/blue]")
        for i, trans in enumerate(result.transcriptions[:2]):  # Show first 2
            sample_text = (
                trans.raw_text[:200] + "..."
                if len(trans.raw_text) > 200
                else trans.raw_text
            )
            console.print(f"[dim]Chunk {i + 1}:[/dim] {sample_text}")

        if len(result.transcriptions) > 2:
            console.print(
                f"[dim]... and {len(result.transcriptions) - 2} more chunks[/dim]"
            )


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
