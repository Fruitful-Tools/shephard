"""Transcription and text correction tasks."""

from prefect import task

from ..config.settings import settings
from ..models.pipeline import AudioChunk, CorrectionResult, TranscriptionResult
from ..services.mock_apis import MockMistralService, MockVoxtralService


@task(retries=2, retry_delay_seconds=10)
async def transcribe_audio_chunk(
    audio_chunk: AudioChunk, _model: str = "voxtral-v1", language: str = "zh-TW"
) -> TranscriptionResult:
    """Transcribe a single audio chunk."""

    if settings.is_development:
        voxtral_service = MockVoxtralService()
        return await voxtral_service.transcribe_chunk(audio_chunk.file_path, language)
    else:
        # TODO: Implement real Voxtral API call
        raise NotImplementedError("Production transcription not implemented")


@task
async def transcribe_chunks_parallel(
    chunks: list[AudioChunk], _model: str = "voxtral-v1", language: str = "zh-TW"
) -> list[TranscriptionResult]:
    """Transcribe multiple audio chunks in parallel."""

    # Use Prefect's built-in concurrency - each chunk runs as a separate task
    transcription_tasks = []

    for chunk in chunks:
        task_result = transcribe_audio_chunk.submit(
            audio_chunk=chunk, language=language
        )
        transcription_tasks.append(task_result)

    # Wait for all transcriptions to complete
    results = []
    for task_result in transcription_tasks:
        result = await task_result.result()
        results.append(result)

    return results


@task(retries=2, retry_delay_seconds=5)
async def correct_transcription(
    transcription: TranscriptionResult,
    target_language: str = "zh-TW",
    model: str = "mistral-medium",
) -> CorrectionResult:
    """Correct and enhance transcribed text."""

    if settings.is_development:
        mistral_service = MockMistralService()
        result = await mistral_service.correct_text(
            transcription.raw_text, target_language, model
        )
        # Update chunk_id to match
        result.chunk_id = transcription.chunk_id
        return result
    else:
        # TODO: Implement real Mistral API call
        raise NotImplementedError("Production text correction not implemented")


@task
async def merge_corrected_texts(corrections: list[CorrectionResult]) -> str:
    """Merge corrected text chunks into a single document."""

    # Sort by chunk_id to maintain order
    sorted_corrections = sorted(corrections, key=lambda x: x.chunk_id)

    merged_text = ""
    for correction in sorted_corrections:
        merged_text += correction.corrected_text
        if not correction.corrected_text.endswith(("。", "！", "？", "\n")):
            merged_text += " "

    return merged_text.strip()
