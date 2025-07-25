"""Demo script to showcase pipeline capabilities."""

import asyncio
import builtins
import contextlib
import os
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config.settings import settings
from .flows.main_flows import (
    run_audio_pipeline,
    run_text_pipeline,
    run_youtube_pipeline,
)
from .models.pipeline import PipelineResult

console = Console()


def show_configuration() -> None:
    """Show current configuration settings."""
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Mock External APIs", str(settings.mock_external_apis))
    table.add_row("Chunk Size (minutes)", str(settings.chunk_size_minutes))
    table.add_row("Default Language", settings.default_language)
    table.add_row("Max Audio Duration (hours)", str(settings.max_audio_duration_hours))
    table.add_row("YouTube Audio Quality", settings.youtube_audio_quality)
    table.add_row("YouTube Audio Format", settings.youtube_audio_format)

    console.print(table)


def configure_api_mode() -> bool:
    """Configure API mode (mock vs real). Returns True if using real APIs."""
    console.print(
        Panel(
            "[bold yellow]⚙️  API Configuration[/bold yellow]\n"
            "Choose whether to use mock APIs (safe for testing) or real external APIs.",
            title="Configuration",
        )
    )

    current_mode = "Mock APIs" if settings.mock_external_apis else "Real APIs"
    console.print(f"Current mode: [bold]{current_mode}[/bold]")

    use_real_apis = Confirm.ask(
        "\n🔗 Use real external APIs? (YouTube downloads, etc.)",
        default=not settings.mock_external_apis,
    )

    if use_real_apis != (not settings.mock_external_apis):
        # Update environment variable for this session
        os.environ["MOCK_EXTERNAL_APIS"] = str(not use_real_apis).lower()
        # Update settings object
        settings.mock_external_apis = not use_real_apis

        mode_text = "Real APIs" if use_real_apis else "Mock APIs"
        console.print(f"✅ Switched to [bold green]{mode_text}[/bold green] mode")

    return use_real_apis


async def demo_text_pipeline() -> PipelineResult:
    """Demo text summarization pipeline."""
    console.print(
        Panel(
            "[bold blue]Demo: Text Summarization Pipeline[/bold blue]\n"
            "Processing text content directly...",
            title="🔤 Text Pipeline",
        )
    )

    sample_text = """
    人工智慧技術在近年來有了飛躍性的發展，特別是在自然語言處理和機器學習領域。
    深度學習模型如GPT和BERT等已經在各種應用場景中展現出驚人的能力，包括文本生成、
    語言翻譯、問答系統等。這些技術的進步不僅改變了我們與機器互動的方式，
    也為各行各業帶來了新的機會和挑戰。在教育領域，AI可以提供個性化的學習體驗；
    在醫療領域，AI輔助診斷系統正在幫助醫生提高診斷準確性；在商業領域，
    智能客服和推薦系統已經成為標配。然而，隨著AI技術的普及，我們也需要考慮
    倫理、隱私和安全等相關議題，確保這些技術能夠造福人類社會。
    """

    result = await run_text_pipeline(
        text_content=sample_text,
        user_id="demo_user",
        summary_instructions="請提供一個簡潔的摘要，重點關注AI技術的應用和影響",
        summary_word_limit=100,
    )

    console.print(f"✅ Status: [green]{result.status}[/green]")
    console.print(f"📊 Credits used: {result.credits_consumed}")
    if result.summary:
        console.print(f"📝 Summary ({result.summary.word_count} words):")
        console.print(f"   {result.summary.summary}")

    return result


async def demo_youtube_pipeline() -> PipelineResult:
    """Demo YouTube video processing pipeline."""
    api_mode = "Real API" if not settings.mock_external_apis else "Mock API"
    console.print(
        Panel(
            f"[bold red]Demo: YouTube Video Pipeline[/bold red]\n"
            f"Mode: {api_mode}\n"
            f"Processing YouTube URL...",
            title="🎥 YouTube Pipeline",
        )
    )

    # Choose URL based on mode
    if settings.mock_external_apis:
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        console.print(f"🎬 Using mock URL: {youtube_url}")
    else:
        # Offer predefined URLs or custom input
        predefined_urls = {
            "1": "https://www.youtube.com/watch?v=qNjZbRuh9bc",  # Test video from earlier
            "2": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll for testing
        }

        console.print("\n📺 Choose a YouTube video:")
        console.print("1. Test video (Chinese sermon)")
        console.print("2. Rick Astley - Never Gonna Give You Up")
        console.print("3. Enter custom URL")

        choice = Prompt.ask("Select option", choices=["1", "2", "3"], default="1")

        if choice in predefined_urls:
            youtube_url = predefined_urls[choice]
        else:
            youtube_url = Prompt.ask("Enter YouTube URL")

        console.print(f"🎬 Using URL: {youtube_url}")

        # Ask for time range if using real APIs
        use_time_range = Confirm.ask(
            "\n⏱️  Download only a specific time range?", default=True
        )

        start_time = None
        end_time = None

        if use_time_range:
            start_time = float(Prompt.ask("Start time (seconds)", default="0"))
            end_time = float(Prompt.ask("End time (seconds)", default="90"))
            console.print(
                f"📹 Will download {start_time}s to {end_time}s ({end_time - start_time}s total)"
            )

    # Configure processing parameters
    chunk_size = (
        2 if not settings.mock_external_apis else 5
    )  # Smaller chunks for real testing

    result = await run_youtube_pipeline(
        youtube_url=youtube_url,
        youtube_start_time=start_time if not settings.mock_external_apis else None,
        youtube_end_time=end_time if not settings.mock_external_apis else None,
        user_id="demo_user",
        chunk_size_minutes=chunk_size,
        summary_instructions="請提供詳細的內容摘要",
        summary_word_limit=200,
    )

    console.print(f"✅ Status: [green]{result.status}[/green]")
    console.print(f"📊 Credits used: {result.credits_consumed}")
    console.print(f"🎵 Audio chunks: {len(result.audio_chunks)}")
    console.print(f"📝 Transcriptions: {len(result.transcriptions)}")

    # Show processing duration if available
    if result.processing_duration:
        console.print(f"⏱️  Processing time: {result.processing_duration:.1f}s")

    # Show more details for real API usage
    if not settings.mock_external_apis and result.audio_chunks:
        console.print("\n🎵 Audio chunk details:")
        for i, chunk in enumerate(result.audio_chunks[:3]):  # Show first 3
            console.print(
                f"   Chunk {i + 1}: {chunk.start_time:.1f}s - {chunk.end_time:.1f}s ({chunk.duration:.1f}s)"
            )
        if len(result.audio_chunks) > 3:
            console.print(f"   ... and {len(result.audio_chunks) - 3} more chunks")

    if result.summary:
        console.print(f"\n📋 Summary ({result.summary.word_count} words):")
        console.print(f"   [italic]{result.summary.summary}[/italic]")
        if not settings.mock_external_apis:
            console.print(f"   Model used: {result.summary.model_used}")

    # Show sample transcription
    if result.transcriptions:
        console.print("\n🎤 Sample transcription:")
        console.print(f"   [dim]{result.transcriptions[0].raw_text[:100]}...[/dim]")

    # Show error message if failed
    if result.error_message:
        console.print(f"\n❌ Error: [red]{result.error_message}[/red]")
        if not settings.mock_external_apis:
            console.print(
                "💡 [yellow]Tip: Some pipeline steps (transcription, correction) are not implemented for production yet.[/yellow]"
            )

    return result


async def demo_audio_pipeline() -> PipelineResult:
    """Demo audio file processing pipeline."""
    console.print(
        Panel(
            "[bold green]Demo: Audio File Pipeline[/bold green]\n"
            "Processing audio file (mocked)...",
            title="🎧 Audio Pipeline",
        )
    )

    # Create a mock audio file
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake audio data for demo")
        audio_path = f.name

    result = await run_audio_pipeline(
        audio_file_path=audio_path,
        user_id="demo_user",
        chunk_size_minutes=10,
        target_language="zh-TW",
    )

    console.print(f"✅ Status: [green]{result.status}[/green]")
    console.print(f"📊 Credits used: {result.credits_consumed}")
    console.print(f"🎵 Audio chunks: {len(result.audio_chunks)}")
    console.print(f"📝 Transcriptions: {len(result.transcriptions)}")

    if result.summary:
        console.print(f"📋 Summary ({result.summary.word_count} words):")
        console.print(f"   {result.summary.summary}")

    # Cleanup
    with contextlib.suppress(builtins.BaseException):
        Path(audio_path).unlink()

    return result


async def interactive_demo() -> None:
    """Run interactive demo with user choices."""
    console.print(
        Panel(
            "[bold magenta]🚀 Shepard Pipeline Interactive Demo[/bold magenta]\n"
            "Choose which pipeline to test and configure API modes",
            title="Shepard Pipeline Demo",
        )
    )

    while True:
        console.print("\n" + "=" * 60 + "\n")

        # Show current configuration
        show_configuration()

        console.print("\n📋 Available demos:")
        console.print("1. 🔤 Text Summarization Pipeline")
        console.print("2. 🎥 YouTube Video Pipeline")
        console.print("3. 🎧 Audio File Pipeline")
        console.print("4. ⚙️  Configure API Mode")
        console.print("5. 🚀 Run All Demos")
        console.print("6. 🚪 Exit")

        choice = Prompt.ask(
            "\nSelect option", choices=["1", "2", "3", "4", "5", "6"], default="2"
        )

        console.print("\n" + "=" * 60 + "\n")

        try:
            if choice == "1":
                await demo_text_pipeline()
            elif choice == "2":
                await demo_youtube_pipeline()
            elif choice == "3":
                await demo_audio_pipeline()
            elif choice == "4":
                configure_api_mode()
                continue
            elif choice == "5":
                await run_all_demos()
            elif choice == "6":
                console.print("👋 Goodbye!")
                break

        except KeyboardInterrupt:
            console.print("\n⚠️  Demo interrupted by user")
            if not Confirm.ask("Continue with demo menu?", default=True):
                break
        except Exception as e:
            console.print(f"❌ Demo failed: {e}")
            if not Confirm.ask("Continue with demo menu?", default=True):
                break

        console.print("\n" + "=" * 60 + "\n")

        if not Confirm.ask("Run another demo?", default=True):
            break

    console.print(
        Panel(
            "[bold green]✅ Demo session completed![/bold green]\n"
            "Thank you for testing the Shepard Pipeline!",
            title="Demo Complete",
        )
    )


async def run_all_demos() -> None:
    """Run all demo pipelines sequentially."""
    console.print(
        Panel(
            "[bold yellow]🎯 Running All Demos[/bold yellow]\n"
            "This will run all three pipelines sequentially",
            title="All Demos",
        )
    )

    # Demo 1: Text Pipeline (fastest)
    await demo_text_pipeline()
    console.print("\n" + "=" * 60 + "\n")

    # Demo 2: YouTube Pipeline
    await demo_youtube_pipeline()
    console.print("\n" + "=" * 60 + "\n")

    # Demo 3: Audio File Pipeline
    await demo_audio_pipeline()


async def main() -> None:
    """Main entry point - choose between interactive and automated demo."""
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Run all demos automatically (for CI/testing)
        await run_all_demos()
    else:
        # Run interactive demo
        await interactive_demo()


if __name__ == "__main__":
    asyncio.run(main())
