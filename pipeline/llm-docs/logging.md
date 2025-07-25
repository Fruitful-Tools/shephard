# Logging Guidelines

This document outlines logging standards and best practices for the Shepard Pipeline project using a **hybrid approach** combining Prefect's native logging with [Loguru](https://loguru.readthedocs.io/).

## Overview

The project uses a **hybrid logging approach** that combines:

- **Prefect's `get_run_logger()`** for tasks and flows (essential for Prefect UI/backend integration)
- **Loguru** for services and utilities (enhanced structured logging capabilities)
- **HybridLogger utility** for components that may run in both contexts

### Key Benefits

- **Prefect Integration**: Flow and task logs appear in Prefect UI with proper context
- **Enhanced Local Logging**: Loguru provides better structured logging for development
- **Flexible Architecture**: Components work both inside and outside Prefect contexts
- **Performance**: Loguru's lazy evaluation for expensive debug operations

## Logging Architecture

### Prefect Tasks and Flows

**Always use `get_run_logger()` in Prefect tasks and flows** - this is required for proper Prefect integration:

```python
from prefect import task, flow, get_run_logger

@task
async def process_audio_chunk(chunk: AudioChunk) -> TranscriptionResult:
    """Prefect tasks must use get_run_logger for UI integration."""
    logger = get_run_logger()
    logger.info(f"Processing audio chunk {chunk.sequence_number}")
    # This log appears in Prefect UI with run context
    return result

@flow
async def audio_pipeline_flow(input_data: PipelineInput) -> PipelineResult:
    """Flows must use get_run_logger for proper backend integration."""
    logger = get_run_logger()
    logger.info(f"Starting audio pipeline for job {input_data.job_id}")
    return result
```

### Services and Utilities

For services and utilities that run outside Prefect context, **use Loguru directly**:

```python
from loguru import logger

class YouTubeService:
    def __init__(self) -> None:
        # Loguru automatically handles logger configuration
        pass

    async def download_audio(self, url: str) -> dict[str, Any]:
        logger.info(f"Downloading audio from {url}")
        try:
            # Process logic
            logger.success(f"Successfully downloaded: {result['title']}")
            return result
        except Exception as e:
            logger.error(f"Failed to download YouTube video {url}: {e}")
            raise
```

### Hybrid Logger for Mixed Contexts

For components that may run both inside and outside Prefect contexts, use the HybridLogger:

```python
from shepard_pipeline.utils.logging import get_hybrid_logger

class ProcessingService:
    def __init__(self) -> None:
        self.logger = get_hybrid_logger()

    async def process_data(self, data: Any) -> Any:
        # Logs to both Prefect (if available) and Loguru
        self.logger.info("Starting data processing")
        try:
            result = await self._process(data)
            self.logger.success("Processing completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise
```

## Log Levels and Usage

### Standard Log Levels

- **`logger.trace()`**: Fine-grained debugging information (disabled in production)
- **`logger.debug()`**: Detailed diagnostic information for development
- **`logger.info()`**: General operational messages about system behavior
- **`logger.success()`**: Loguru-specific level for successful operations
- **`logger.warning()`**: Warning messages for recoverable issues
- **`logger.error()`**: Error messages for failures that don't stop execution
- **`logger.critical()`**: Critical errors that may cause system failure

### Usage Guidelines

#### Information Logging
```python
# Flow/pipeline progress
logger.info(f"Starting YouTube pipeline for job {job_id}")
logger.info(f"Transcribing {len(chunks)} audio chunks...")
logger.info(f"Pipeline completed successfully for job {job_id}")

# Processing milestones
logger.info(f"Downloaded audio: {title} ({duration:.1f}s, {file_size:.1f}MB)")
logger.info(f"Generated summary with {word_count} words")
```

#### Success Logging
```python
# Completed operations
logger.success(f"Successfully downloaded: {result['title']}")
logger.success(f"Audio transcription completed in {elapsed_time:.2f}s")
logger.success(f"Pipeline job {job_id} completed with {credits_consumed} credits")
```

#### Error Logging
```python
# Recoverable errors
logger.warning("Summary validation failed, but continuing...")
logger.warning(f"Chunk {chunk_id} transcription quality below threshold")

# Critical errors
logger.error(f"Failed to download YouTube video {url}: {e}")
logger.error(f"Pipeline failed: {str(e)}")
logger.critical(f"Database connection lost: {e}")
```

#### Debug Logging
```python
# Development debugging
logger.debug(f"Processing chunk {chunk.sequence_number} with {chunk.duration}s duration")
logger.debug(f"API request payload: {payload}")
logger.trace(f"Raw API response: {response}")
```

## Configuration

### Development Configuration

For local development, Loguru uses sensible defaults with structured output:

```python
from loguru import logger

# Default configuration includes:
# - Colorized console output
# - Timestamp, level, module path
# - Automatic JSON serialization for structured data
# - Integration with Prefect run context
```

### Production Configuration

Production logging can be configured through environment variables:

```python
import os
from loguru import logger

# Production configuration
if os.getenv("ENVIRONMENT") == "production":
    logger.remove()  # Remove default handler
    logger.add(
        sink=sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        level="INFO",
        serialize=True,  # JSON output for log aggregation
        backtrace=False,
        diagnose=False,
    )
```

## Integration Patterns

### Prefect Task Logging

```python
from loguru import logger
from prefect import task

@task(retries=3, retry_delay_seconds=30)
async def transcribe_audio_chunk(chunk: AudioChunk) -> TranscriptionResult:
    """Transcribe audio chunk with comprehensive logging."""
    logger.info(f"Starting transcription for chunk {chunk.sequence_number}")

    try:
        # Log processing details
        logger.debug(f"Chunk details: {chunk.duration}s, {chunk.file_size} bytes")

        result = await transcription_service.transcribe(chunk)

        # Log success metrics
        logger.success(
            f"Transcription completed: {len(result.text)} chars, "
            f"confidence: {result.confidence:.2f}"
        )

        return result

    except Exception as e:
        # Log error with context
        logger.error(
            f"Transcription failed for chunk {chunk.sequence_number}: {e}",
            extra={"chunk_id": chunk.id, "chunk_duration": chunk.duration}
        )
        raise
```

### Service Class Logging

```python
from loguru import logger

class MockTranscriptionService:
    """Mock service with integrated logging."""

    async def transcribe_audio(self, audio_path: str) -> TranscriptionResult:
        logger.info(f"Mock transcribing audio file: {audio_path}")

        # Simulate processing
        await asyncio.sleep(0.1)

        result = TranscriptionResult(
            text="Mock transcription text",
            confidence=0.95,
            language="en",
            duration=30.0
        )

        logger.success(f"Mock transcription completed: {len(result.text)} characters")
        return result
```

### Error Handling and Logging

```python
from loguru import logger

async def process_pipeline_with_logging(input_data: PipelineInput) -> PipelineResult:
    """Process pipeline with comprehensive error logging."""
    logger.info(f"Starting pipeline for job {input_data.job_id}")

    try:
        # Process pipeline steps
        result = await execute_pipeline_steps(input_data)

        logger.success(f"Pipeline completed: job {input_data.job_id}")
        return result

    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise

    except ExternalServiceError as e:
        logger.error(f"External service failure: {e}")
        raise

    except Exception as e:
        logger.critical(f"Unexpected pipeline failure: {e}")
        raise

    finally:
        # Always log completion
        logger.debug(f"Pipeline processing completed for job {input_data.job_id}")
```

## Best Practices

### 1. Structured Logging

Use Loguru's automatic serialization for complex data:

```python
# Good - automatic JSON serialization
logger.info("Processing complete", extra={
    "job_id": job.id,
    "duration": elapsed_time,
    "credits_consumed": credits,
    "chunks_processed": len(chunks)
})

# Avoid - string formatting for structured data
logger.info(f"Processing complete: job={job.id}, duration={elapsed_time}")
```

### 2. Contextual Information

Include relevant context in log messages:

```python
# Good - includes context
logger.error(f"Failed to transcribe chunk {chunk.sequence_number}: {e}")

# Avoid - missing context
logger.error(f"Transcription failed: {e}")
```

### 3. Performance Considerations

Use lazy evaluation for expensive operations:

```python
# Good - lazy evaluation
logger.debug("API payload: {}", lambda: json.dumps(large_payload, indent=2))

# Avoid - eager evaluation
logger.debug(f"API payload: {json.dumps(large_payload, indent=2)}")
```

### 4. Sensitive Data

Never log sensitive information:

```python
# Good - sanitized logging
logger.info(f"Processing user request for user_id: {user_id}")

# Avoid - sensitive data in logs
logger.info(f"Processing request: {api_key}, {user_email}")
```

## Migration from Standard Logging

### Automatic Migration

The logging system automatically handles both Loguru and standard logging:

```python
# Old code using get_run_logger still works
from prefect import get_run_logger
logger = get_run_logger()
logger.info("This still works")

# New code using Loguru
from loguru import logger
logger.info("This is preferred")
```

### Service Migration Pattern

For services, replace standard logging setup:

```python
# Old approach
import logging
logger = logging.getLogger(__name__)

# New approach
from loguru import logger
# No additional setup needed
```

## Testing

### Test Logging

In tests, Loguru output can be captured:

```python
import pytest
from loguru import logger

def test_logging_output(caplog):
    """Test that captures log output."""
    with caplog.at_level("INFO"):
        logger.info("Test message")
        assert "Test message" in caplog.text
```

### Mock Logging

For unit tests, logging can be disabled or redirected:

```python
from loguru import logger

@pytest.fixture
def disable_logging():
    """Disable logging for tests."""
    logger.disable("shepard_pipeline")
    yield
    logger.enable("shepard_pipeline")
```

## Troubleshooting

### Common Issues

1. **Missing log output**: Ensure Loguru is properly imported
2. **Performance impact**: Use lazy evaluation for debug logs
3. **Log format**: Check environment configuration for production
4. **Integration issues**: Verify Prefect context is available

### Debugging Logging

Enable trace-level logging for detailed debugging:

```python
from loguru import logger

# Temporary trace logging
logger.add(sys.stderr, level="TRACE", filter="shepard_pipeline")
```
