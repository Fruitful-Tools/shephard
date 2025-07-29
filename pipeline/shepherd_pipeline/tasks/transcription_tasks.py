"""Transcription-related Prefect tasks."""

from prefect import get_run_logger, task

from ..services.llm_provider.schema import (
    AudioChunk,
    CorrectionResult,
    TranscriptionResult,
)
from ..services.model_factory import ModelFactory
from ..services.translation_service import ChineseTranslationService


@task(
    retries=3,
    retry_delay_seconds=[4, 8, 16],  # exponential backoff
    retry_jitter_factor=0.1,
)
async def transcribe_audio_chunk(
    audio_chunk: AudioChunk,
    model: str = "voxtral-mini-latest",
    language: str = "zh-TW",
) -> TranscriptionResult:
    """Transcribe a single audio chunk and translate to Traditional Chinese."""
    logger = get_run_logger()

    # Use the model factory to create appropriate transcription service
    transcription_service = ModelFactory.create_transcription_service(model)
    service_language = "zh" if language.startswith("zh") else language
    result = await transcription_service.transcribe_audio(
        audio_chunk.file_path, service_language
    )

    # Handle Voxtral failures with fallback to OpenAI
    if result.failure_reason:
        logger.warning(
            f"Transcription failed for chunk {audio_chunk.file_path}, falling back to OpenAI Whisper"
        )
        # Fallback to OpenAI
        fallback_service = ModelFactory.create_transcription_service(
            "gpt-4o-mini-transcribe"
        )
        openai_language = "zh" if language.startswith("zh") else language
        result = await fallback_service.transcribe_audio(
            audio_chunk.file_path, openai_language
        )

    if result.failure_reason:
        raise RuntimeError(
            f"Transcription failed for chunk {audio_chunk.file_path}: {result.failure_reason}"
        )

    # Translate to Traditional Chinese (Taiwan) using OpenCC
    translation_service = ChineseTranslationService()
    translated_text = translation_service.to_traditional_chinese(result.raw_text)

    # Update the result with translated text
    result.raw_text = translated_text
    result.language = language  # Keep the original language setting

    logger.info(
        f"Text converted to Traditional Chinese (TW): {len(translated_text)} chars, transcription preview {audio_chunk.chunk_id}: {translated_text[:100]}..."
    )

    return result


@task
async def transcribe_chunks_parallel(
    chunks: list[AudioChunk],
    model: str = "voxtral-mini-latest",
    language: str = "zh-TW",
) -> list[TranscriptionResult]:
    """Transcribe multiple audio chunks in parallel."""
    logger = get_run_logger()
    logger.info(f"Starting parallel transcription of {len(chunks)} chunks")

    tasks = [
        transcribe_audio_chunk.submit(audio_chunk=chunk, model=model, language=language)
        for chunk in chunks
    ]
    results: list[TranscriptionResult] = [task.result() for task in tasks]  # type: ignore

    logger.info(f"Completed transcription of {len(results)} chunks")
    return results


@task(
    retries=3,
    retry_delay_seconds=[4, 8, 16],  # exponential backoff
    retry_jitter_factor=0.1,
)
async def correct_transcription(
    transcription: TranscriptionResult,
    target_language: str = "zh-TW",
    model: str = "mistral-small-latest",
) -> CorrectionResult:
    """Correct and enhance transcribed text with Christian context."""
    logger = get_run_logger()

    # Use model factory to create appropriate service
    text_processor = ModelFactory.create_text_processor(model=model)

    result = await text_processor.correct_text(
        transcription.raw_text, target_language, model
    )
    if result.failure_reason:
        raise RuntimeError(
            f"Correction failed for {transcription.raw_text}: {result.failure_reason}"
        )

    # Log correction preview
    logger.info(
        f"Correction preview for {transcription.raw_text[:100]}...: {result.corrected_text[:100]}..."
    )
    return result


@task
async def correct_transcriptions_parallel(
    transcriptions: list[TranscriptionResult],
    target_language: str = "zh-TW",
    model: str = "mistral-small-latest",
) -> list[CorrectionResult]:
    """Correct multiple transcriptions in parallel."""
    logger = get_run_logger()
    logger.info(f"Starting parallel correction of {len(transcriptions)} transcriptions")

    tasks = [
        correct_transcription.submit(
            transcription=transcription, target_language=target_language, model=model
        )
        for transcription in transcriptions
    ]
    results: list[CorrectionResult] = [task.result() for task in tasks]  # type: ignore

    logger.info(f"Completed correction of {len(results)} transcriptions")
    return results


@task
async def merge_corrected_texts(corrections: list[CorrectionResult]) -> str:
    """Merge corrected text chunks into a single document."""

    # Sort by chunk_id to maintain order
    merged_text = ""
    for correction in corrections:
        merged_text += correction.corrected_text
        if not correction.corrected_text.endswith(("。", "！", "？", "\n")):
            merged_text += " "

    return merged_text.strip()
