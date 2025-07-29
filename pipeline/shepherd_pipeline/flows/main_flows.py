"""Main pipeline flows for different entry points."""

from datetime import UTC, datetime
from uuid import uuid4

from prefect import flow, get_run_logger

from ..models.pipeline import (
    JobStatus,
    PipelineInput,
    PipelineResult,
)
from ..tasks.audio_tasks import (
    chunk_audio,
    download_youtube_audio,
)
from ..tasks.summarization_tasks import summarize_text, validate_summary_quality
from ..tasks.transcription_tasks import (
    correct_transcriptions_parallel,
    merge_corrected_texts,
    transcribe_chunks_parallel,
)
from ..utils.artifact_manager import ArtifactManager


@flow(name="youtube-pipeline", retries=3, retry_delay_seconds=30)
async def youtube_pipeline_flow(
    pipeline_input: PipelineInput, use_mock: bool = False
) -> PipelineResult:
    """Process YouTube video URL through complete pipeline with resume capability."""
    logger = get_run_logger()
    job_id = str(pipeline_input.job_id or uuid4())

    logger.info(f"Starting fresh YouTube pipeline for job {job_id}")

    result = PipelineResult(
        job_id=pipeline_input.job_id,
        user_id=pipeline_input.user_id,
        status=JobStatus.RUNNING,
        started_at=datetime.now(UTC),
        input_params=pipeline_input,
    )
    artifact_manager = ArtifactManager()

    try:
        # Step 1: Download YouTube audio
        logger.info("Downloading YouTube audio...")
        audio_metadata = await download_youtube_audio(  # type: ignore[misc]
            pipeline_input.youtube_url,
            pipeline_input.youtube_start_time,
            pipeline_input.youtube_end_time,
            use_mock,
        )

        # Step 2: Chunk audio
        logger.info("Chunking audio...")
        chunks = await chunk_audio(
            audio_metadata,
            pipeline_input.chunk_size_minutes,
            use_mock=use_mock,
        )
        result.audio_chunks = chunks

        # Step 3: Transcribe chunks
        logger.info(f"Transcribing {len(chunks)} audio chunks...")
        transcriptions = await transcribe_chunks_parallel(
            chunks,
            model=pipeline_input.transcription_model,
            language=pipeline_input.target_language,
        )

        result.transcriptions = transcriptions

        # Step 4: Correct transcriptions
        logger.info("Correcting transcriptions...")
        corrections = await correct_transcriptions_parallel(
            transcriptions,
            target_language=pipeline_input.target_language,
            model=pipeline_input.correction_model,
        )

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
        audio_duration_hours = audio_metadata.duration / 3600
        result.credits_consumed = max(1, int(audio_duration_hours))

        logger.info(f"Pipeline completed successfully for job {job_id}")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        result.status = JobStatus.FAILED
        result.error_message = str(e)
        result.completed_at = datetime.now(UTC)

    finally:
        artifact_manager.remove_chunks(
            audio_metadata, pipeline_input.chunk_size_minutes
        )

    return result
