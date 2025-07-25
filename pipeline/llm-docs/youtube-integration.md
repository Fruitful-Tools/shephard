# YouTube Integration Documentation

This document details the implementation of real YouTube video download functionality using yt-dlp, including time range extraction and the dual mock/production mode system.

## Overview

The Shepard Pipeline now supports downloading YouTube videos with precise time range control, using yt-dlp for production downloads while maintaining mock API compatibility for development.

## Architecture

### Service Layer

#### YouTubeService (`services/youtube_service.py`)
- **Real Implementation**: Uses yt-dlp for actual YouTube downloads
- **Time Range Support**: Implements `download_sections` for precise start/end time extraction
- **Async Wrapper**: Uses `asyncio.to_thread()` for non-blocking yt-dlp operations
- **Format Control**: Downloads best audio quality and converts to MP3 at 192kbps
- **Error Handling**: Comprehensive error handling with detailed logging

#### MockYouTubeService (`services/mock_apis.py`)
- **Development Mode**: Provides realistic mock responses for testing
- **Time Range Simulation**: Calculates durations based on provided start/end times
- **File Simulation**: Creates mock audio files for testing downstream processes

### Configuration System

#### Runtime API Toggle
The system supports switching between mock and real APIs via the `MOCK_EXTERNAL_APIS` environment variable:

**Mock Mode (Development)**:
```env
MOCK_EXTERNAL_APIS=true
```

**Production Mode**:
```env
MOCK_EXTERNAL_APIS=false
```

#### YouTube-Specific Settings
New configuration options in `config/settings.py`:

```python
# YouTube Service Configuration
youtube_audio_quality: str = "192K"
youtube_audio_format: str = "mp3"
youtube_max_duration_hours: int = 6
```

### Data Model Enhancements

#### PipelineInput Model Updates
Added support for YouTube time range parameters:

```python
# YouTube-specific parameters
youtube_start_time: float | None = Field(default=None, ge=0)
youtube_end_time: float | None = Field(default=None, ge=0)
```

#### Validation
- Ensures `youtube_end_time > youtube_start_time` when both are specified
- Validates time values are non-negative
- Maintains backward compatibility (defaults to full video)

## Implementation Details

### yt-dlp Integration

#### Download Configuration
```python
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": str(output_path_obj.with_suffix("")),
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]
}
```

#### Time Range Extraction
Uses yt-dlp's `download_sections` feature for precise time control:

```python
if start_time is not None or end_time is not None:
    sections = []
    if start_time is not None and end_time is not None:
        sections.append(f"*{start_time}-{end_time}")
    elif start_time is not None:
        sections.append(f"*{start_time}-inf")
    elif end_time is not None:
        sections.append(f"*0-{end_time}")

    if sections:
        ydl_opts["download_sections"] = sections
```

### Audio Processing Pipeline

#### Enhanced Chunking
Updated `audio_tasks.py` to support production audio chunking using pydub:

```python
# Production audio chunking using pydub
if not PYDUB_AVAILABLE:
    raise ImportError("pydub is required for production audio chunking")

audio = AudioSegment.from_file(str(audio_path))
chunk_duration_ms = chunk_size_minutes * 60 * 1000
pydub_chunks = make_chunks(audio, chunk_duration_ms)
```

#### File Management
- Automatic cleanup of temporary files
- Dynamic file extension detection (.mp3, .m4a, .webm, .ogg)
- Proper path handling for both mock and real files

### Flow Integration

#### Task Updates
The `download_youtube_audio` task now accepts time parameters:

```python
@task(retries=2, retry_delay_seconds=5)
async def download_youtube_audio(
    youtube_url: HttpUrl,
    output_dir: str,
    start_time: float | None = None,
    end_time: float | None = None,
) -> dict[str, Any]:
```

#### Flow Orchestration
Updated `youtube_pipeline_flow` to pass time parameters through the pipeline:

```python
audio_metadata = await download_youtube_audio(
    pipeline_input.youtube_url,
    temp_dir,
    pipeline_input.youtube_start_time,
    pipeline_input.youtube_end_time,
)
```

## Usage Examples

### Basic Usage
```python
from shepard_pipeline.flows.main_flows import run_youtube_pipeline

# Download entire video
result = await run_youtube_pipeline(
    youtube_url="https://www.youtube.com/watch?v=example",
    user_id="test_user"
)

# Download specific time range (30s to 90s)
result = await run_youtube_pipeline(
    youtube_url="https://www.youtube.com/watch?v=example",
    youtube_start_time=30,
    youtube_end_time=90,
    user_id="test_user"
)
```

### Interactive Demo
The enhanced `demo.py` provides comprehensive testing:

```bash
# Interactive mode with API toggle
uv run python -m shepard_pipeline.demo

# Automated testing mode
uv run python -m shepard_pipeline.demo --auto
```

#### Demo Features
- **API Mode Toggle**: Switch between mock and real APIs at runtime
- **URL Selection**: Choose from predefined URLs or enter custom ones
- **Time Range Configuration**: Interactive setup of start/end times
- **Detailed Results**: Shows chunk information, processing times, and errors

## Testing Strategy

### Mock API Testing
- Simulates realistic download scenarios
- Tests time range calculations
- Validates data flow without external dependencies
- Safe for CI/CD environments

### Real API Testing
- Validates actual yt-dlp integration
- Tests time range extraction accuracy
- Verifies audio quality and format conversion
- Requires network connectivity

### Error Handling
- Network timeouts and connection errors
- Invalid YouTube URLs
- Restricted or private videos
- Time range validation errors

## Dependencies

### Production Dependencies
```toml
[dependencies]
yt-dlp = ">=2023.12.30"  # YouTube download functionality
pydub = ">=0.25.1"       # Audio processing and chunking
```

### System Requirements
- **ffmpeg**: Required by yt-dlp for audio extraction and conversion
- **Python 3.12+**: For proper typing and datetime handling

## Type Safety

### MyPy Compatibility
All new code includes proper type annotations:
- Third-party import handling with `# type: ignore[import-untyped]`
- Explicit type annotations for yt-dlp return values
- Union types for optional parameters

### Pydantic Integration
- Runtime validation of YouTube URLs
- Time parameter validation with proper constraints
- Backward-compatible model updates

## Performance Considerations

### Async Implementation
- Non-blocking yt-dlp operations using `asyncio.to_thread()`
- Parallel processing support for multiple downloads
- Proper resource cleanup and error handling

### Memory Management
- Streaming audio processing where possible
- Temporary file cleanup in error scenarios
- Configurable chunk sizes for memory control

### Network Optimization
- Retry logic for network failures
- Configurable timeout settings
- Bandwidth-efficient audio quality selection

## Security Considerations

### Input Validation
- URL validation using Pydantic HttpUrl
- Time parameter bounds checking
- Prevention of path traversal attacks

### File System Safety
- Temporary directory isolation
- Automatic cleanup of downloaded files
- Secure file naming with UUIDs

## Future Enhancements

### Planned Features
1. **Playlist Support**: Download multiple videos from playlists
2. **Quality Selection**: Runtime audio quality configuration
3. **Subtitle Extraction**: Download and process video subtitles
4. **Caching Layer**: Cache downloaded content for repeated processing
5. **Batch Processing**: Parallel download of multiple videos

### Integration Points
1. **Cloud Storage**: Direct upload to S3/GCS after download
2. **Webhook Notifications**: Status updates for long downloads
3. **Rate Limiting**: Respect YouTube's rate limits
4. **Analytics**: Download success/failure tracking

This implementation provides a robust, production-ready YouTube integration while maintaining the flexibility and testability of the mock-first development approach.
