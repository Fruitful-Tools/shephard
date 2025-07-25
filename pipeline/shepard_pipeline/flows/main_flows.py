"""Main pipeline flows for different entry points."""

from datetime import UTC, datetime
import tempfile
from typing import Any
from uuid import uuid4

from prefect import flow, get_run_logger
from pydantic import HttpUrl

from ..models.pipeline import (
    EntryPointType,
    JobStatus,
    PipelineInput,
    PipelineResult,
)
from ..tasks.audio_tasks import (
    chunk_audio,
    cleanup_temp_files,
    download_youtube_audio,
    validate_audio_file,
)
from ..tasks.summarization_tasks import summarize_text, validate_summary_quality
from ..tasks.transcription_tasks import (
    correct_transcription,
    merge_corrected_texts,
    transcribe_audio_chunk,
)


@flow(name="youtube-pipeline", retries=1, retry_delay_seconds=30)
async def youtube_pipeline_flow(pipeline_input: PipelineInput) -> PipelineResult:
    """Process YouTube video URL through complete pipeline."""
    logger = get_run_logger()
    logger.info(f"Starting YouTube pipeline for job {pipeline_input.job_id}")

    result = PipelineResult(
        job_id=pipeline_input.job_id or uuid4(),
        user_id=pipeline_input.user_id,
        status=JobStatus.RUNNING,
        entry_point=EntryPointType.YOUTUBE,
        started_at=datetime.now(UTC),
        input_params=pipeline_input,
    )

    temp_files = []

    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Download YouTube audio
            logger.info("Downloading YouTube audio...")
            audio_metadata = await download_youtube_audio(  # type: ignore[misc]
                pipeline_input.youtube_url,
                temp_dir,
                pipeline_input.youtube_start_time,
                pipeline_input.youtube_end_time,
            )
            temp_files.append(audio_metadata["file_path"])

            # Step 2: Chunk audio
            logger.info("Chunking audio...")
            chunks = await chunk_audio(
                audio_metadata["file_path"], pipeline_input.chunk_size_minutes
            )
            result.audio_chunks = chunks
            temp_files.extend([chunk.file_path for chunk in chunks])

            # Step 3: Transcribe chunks
            logger.info(f"Transcribing {len(chunks)} audio chunks...")
            transcriptions = []
            for chunk in chunks:
                transcription = await transcribe_audio_chunk(
                    chunk,
                    pipeline_input.transcription_model,
                    pipeline_input.target_language,
                )
                transcriptions.append(transcription)

            result.transcriptions = transcriptions

            # Step 4: Correct transcriptions
            logger.info("Correcting transcriptions...")
            corrections = []
            for transcription in transcriptions:
                correction = await correct_transcription(
                    transcription,
                    pipeline_input.target_language,
                    pipeline_input.correction_model,
                )
                corrections.append(correction)

            result.corrections = corrections

            # Step 5: Merge corrected texts
            logger.info("Merging corrected texts...")
            merged_text = await merge_corrected_texts(corrections)

            # Step 6: Generate summary
            logger.info("Generating summary...")
            summary = await summarize_text(
                merged_text,
                pipeline_input.summary_instructions,
                pipeline_input.summary_word_limit,
                pipeline_input.summarization_model,
            )

            # Step 7: Validate summary
            is_valid = await validate_summary_quality(summary, merged_text)
            if not is_valid:
                logger.warning("Summary validation failed, but continuing...")

            result.summary = summary
            result.status = JobStatus.COMPLETED
            result.completed_at = datetime.now(UTC)

            # Calculate credits consumed (mock calculation)
            audio_duration_hours = audio_metadata["duration"] / 3600
            result.credits_consumed = max(1, int(audio_duration_hours))

            logger.info(
                f"Pipeline completed successfully for job {pipeline_input.job_id}"
            )

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        result.status = JobStatus.FAILED
        result.error_message = str(e)
        result.completed_at = datetime.now(UTC)

    finally:
        # Cleanup temporary files
        if temp_files:
            await cleanup_temp_files(temp_files)

    return result


@flow(name="audio-file-pipeline", retries=1, retry_delay_seconds=30)
async def audio_file_pipeline_flow(pipeline_input: PipelineInput) -> PipelineResult:
    """Process uploaded audio file through complete pipeline."""
    logger = get_run_logger()
    logger.info(f"Starting audio file pipeline for job {pipeline_input.job_id}")

    result = PipelineResult(
        job_id=pipeline_input.job_id or uuid4(),
        user_id=pipeline_input.user_id,
        status=JobStatus.RUNNING,
        entry_point=EntryPointType.AUDIO_FILE,
        started_at=datetime.now(UTC),
        input_params=pipeline_input,
    )

    temp_files = []

    try:
        # Step 1: Validate audio file
        logger.info("Validating audio file...")
        audio_metadata = await validate_audio_file(pipeline_input.audio_file_path)  # type: ignore[misc]

        # Step 2: Chunk audio
        logger.info("Chunking audio...")
        chunks = await chunk_audio(  # type: ignore[misc]
            pipeline_input.audio_file_path, pipeline_input.chunk_size_minutes
        )
        result.audio_chunks = chunks
        temp_files.extend([chunk.file_path for chunk in chunks])

        # Steps 3-7: Same as YouTube pipeline
        # Transcribe chunks
        logger.info(f"Transcribing {len(chunks)} audio chunks...")
        transcriptions = []
        for chunk in chunks:
            transcription = await transcribe_audio_chunk(
                chunk,
                pipeline_input.transcription_model,
                pipeline_input.target_language,
            )
            transcriptions.append(transcription)

        result.transcriptions = transcriptions

        # Correct transcriptions
        logger.info("Correcting transcriptions...")
        corrections = []
        for transcription in transcriptions:
            correction = await correct_transcription(
                transcription,
                pipeline_input.target_language,
                pipeline_input.correction_model,
            )
            corrections.append(correction)

        result.corrections = corrections

        # Merge and summarize
        merged_text = await merge_corrected_texts(corrections)
        summary = await summarize_text(
            merged_text,
            pipeline_input.summary_instructions,
            pipeline_input.summary_word_limit,
            pipeline_input.summarization_model,
        )

        is_valid = await validate_summary_quality(summary, merged_text)
        if not is_valid:
            logger.warning("Summary validation failed, but continuing...")

        result.summary = summary
        result.status = JobStatus.COMPLETED
        result.completed_at = datetime.now(UTC)

        # Calculate credits
        audio_duration_hours = audio_metadata["duration"] / 3600
        result.credits_consumed = max(1, int(audio_duration_hours))

        logger.info(f"Pipeline completed successfully for job {pipeline_input.job_id}")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        result.status = JobStatus.FAILED
        result.error_message = str(e)
        result.completed_at = datetime.now(UTC)

    finally:
        # Cleanup temporary files
        if temp_files:
            await cleanup_temp_files(temp_files)

    return result


@flow(name="text-summary-pipeline", retries=1, retry_delay_seconds=30)
async def text_summary_pipeline_flow(pipeline_input: PipelineInput) -> PipelineResult:
    """Process text input for summarization only."""
    logger = get_run_logger()
    logger.info(f"Starting text summary pipeline for job {pipeline_input.job_id}")

    result = PipelineResult(
        job_id=pipeline_input.job_id or uuid4(),
        user_id=pipeline_input.user_id,
        status=JobStatus.RUNNING,
        entry_point=EntryPointType.TEXT,
        started_at=datetime.now(UTC),
        input_params=pipeline_input,
    )

    try:
        # Step 1: Generate summary directly from text
        logger.info("Generating summary from text...")
        summary = await summarize_text(  # type: ignore[misc]
            pipeline_input.text_content,
            pipeline_input.summary_instructions,
            pipeline_input.summary_word_limit,
            pipeline_input.summarization_model,
        )

        # Step 2: Validate summary
        is_valid = await validate_summary_quality(summary, pipeline_input.text_content)  # type: ignore[misc]
        if not is_valid:
            logger.warning("Summary validation failed, but continuing...")

        result.summary = summary
        result.status = JobStatus.COMPLETED
        result.completed_at = datetime.now(UTC)

        # Text processing consumes 1 credit regardless of length
        result.credits_consumed = 1

        logger.info(
            f"Text pipeline completed successfully for job {pipeline_input.job_id}"
        )

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        result.status = JobStatus.FAILED
        result.error_message = str(e)
        result.completed_at = datetime.now(UTC)

    return result


@flow(name="main-pipeline-dispatcher", retries=0)
async def main_pipeline_flow(pipeline_input: PipelineInput) -> PipelineResult:
    """Main dispatcher flow that routes to appropriate sub-flow based on entry point."""
    logger = get_run_logger()
    logger.info(f"Dispatching pipeline for entry point: {pipeline_input.entry_point}")

    # Route to appropriate sub-flow
    if pipeline_input.entry_point == EntryPointType.YOUTUBE:
        return await youtube_pipeline_flow(pipeline_input)
    elif pipeline_input.entry_point == EntryPointType.AUDIO_FILE:
        return await audio_file_pipeline_flow(pipeline_input)
    elif pipeline_input.entry_point == EntryPointType.TEXT:
        return await text_summary_pipeline_flow(pipeline_input)
    else:
        raise ValueError(f"Unsupported entry point: {pipeline_input.entry_point}")


# Convenience functions for running flows
async def run_youtube_pipeline(
    youtube_url: str,
    user_id: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> PipelineResult:
    """Convenience function to run YouTube pipeline."""
    pipeline_input = PipelineInput(
        entry_point=EntryPointType.YOUTUBE,
        youtube_url=HttpUrl(youtube_url),
        user_id=user_id,
        **kwargs,
    )
    return await main_pipeline_flow(pipeline_input)


async def run_audio_pipeline(
    audio_file_path: str,
    user_id: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> PipelineResult:
    """Convenience function to run audio file pipeline."""
    pipeline_input = PipelineInput(
        entry_point=EntryPointType.AUDIO_FILE,
        audio_file_path=audio_file_path,
        user_id=user_id,
        **kwargs,
    )
    return await main_pipeline_flow(pipeline_input)


async def run_text_pipeline(
    text_content: str,
    user_id: str | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> PipelineResult:
    """Convenience function to run text summary pipeline."""
    pipeline_input = PipelineInput(
        entry_point=EntryPointType.TEXT,
        text_content=text_content,
        user_id=user_id,
        **kwargs,
    )
    return await main_pipeline_flow(pipeline_input)
