"""Demo script to showcase pipeline capabilities."""

import asyncio
import builtins
import contextlib
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .flows.main_flows import (
    run_audio_pipeline,
    run_text_pipeline,
    run_youtube_pipeline,
)
from .models.pipeline import PipelineResult

console = Console()


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
    console.print(
        Panel(
            "[bold red]Demo: YouTube Video Pipeline[/bold red]\n"
            "Processing YouTube URL (mocked)...",
            title="🎥 YouTube Pipeline",
        )
    )

    # Mock YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    result = await run_youtube_pipeline(
        youtube_url=youtube_url,
        user_id="demo_user",
        chunk_size_minutes=5,
        summary_instructions="請提供詳細的內容摘要",
        summary_word_limit=200,
    )

    console.print(f"✅ Status: [green]{result.status}[/green]")
    console.print(f"📊 Credits used: {result.credits_consumed}")
    console.print(f"🎵 Audio chunks: {len(result.audio_chunks)}")
    console.print(f"📝 Transcriptions: {len(result.transcriptions)}")

    if result.summary:
        console.print(f"📋 Summary ({result.summary.word_count} words):")
        console.print(f"   {result.summary.summary}")

    # Show sample transcription
    if result.transcriptions:
        console.print("🎤 Sample transcription:")
        console.print(f"   {result.transcriptions[0].raw_text}")

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


async def main() -> None:
    """Run all demo pipelines."""
    console.print(
        Panel(
            "[bold magenta]🚀 Shepard Pipeline Demo[/bold magenta]\n"
            "Demonstrating all three entry points with mocked APIs",
            title="Shepard Pipeline Demo",
        )
    )

    console.print("\n" + "=" * 60 + "\n")

    # Demo 1: Text Pipeline (fastest)
    await demo_text_pipeline()

    console.print("\n" + "=" * 60 + "\n")

    # Demo 2: YouTube Pipeline
    await demo_youtube_pipeline()

    console.print("\n" + "=" * 60 + "\n")

    # Demo 3: Audio File Pipeline
    await demo_audio_pipeline()

    console.print("\n" + "=" * 60 + "\n")

    console.print(
        Panel(
            "[bold green]✅ All demos completed successfully![/bold green]\n"
            "The pipeline is ready for integration with the frontend.\n"
            "All external APIs are mocked for local development.",
            title="Demo Complete",
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
