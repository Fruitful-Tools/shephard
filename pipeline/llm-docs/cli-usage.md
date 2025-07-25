# Shepherd Pipeline CLI Usage Guide

The Shepherd Pipeline CLI provides a powerful command-line interface for processing YouTube videos through AI-powered transcription and summarization pipelines.

> **Note**: Currently, only YouTube video processing is fully implemented. Audio file and text processing pipelines are planned for future releases.

## Installation

```bash
# Install dependencies (see Local Development Setup for complete setup)
uv sync

# Verify installation
uv run python -m shepherd_pipeline.cli --help
```

> **Environment Setup**: For Python environment setup (pyenv, uv), see [Python Environment Setup](python-env.md). For Docker infrastructure and project setup, see [Local Development Setup](local-dev.md).

## Commands Overview

### YouTube Video Processing

Process YouTube videos with optional time range selection and export capabilities.

```bash
uv run python -m shepherd_pipeline.cli youtube URL [OPTIONS]
```

**Arguments:**
- `URL`: YouTube video URL to process (required)

**Options:**
- `--start FLOAT`: Start time in seconds (optional)
- `--end FLOAT`: End time in seconds (optional)
- `--export-transcript PATH`: Export transcript to file (use {timestamp} for auto-timestamp)
- `--export-summary PATH`: Export summary to file (use {timestamp} for auto-timestamp)
- `--transcription-provider TEXT`: Transcription provider [mistral/openai] (default: mistral)
- `--transcription-model TEXT`: Transcription model name (default: voxtral-mini-latest)
- `--correction-provider TEXT`: Correction provider [mistral/openai] (default: mistral)
- `--correction-model TEXT`: Correction model name (default: mistral-medium-2505)
- `--summary-provider TEXT`: Summary provider [mistral/openai] (default: mistral)
- `--summary-model TEXT`: Summary model name (default: mistral-medium-2505)
- `--mock/--no-mock`: Use mock APIs instead of real ones (default: False)
- `--audio-chunk-interval INT`: Audio chunk interval in minutes (default: 10)
- `--summary-word-count INT`: Target word count for summary (default: 1500)
- `--summary-instruction TEXT`: Custom summary instructions (optional)
- `--user TEXT`: User ID (optional)
- `--lang TEXT`: Target language (default: zh-TW)

### List Available Models

Display all available AI models grouped by provider.

```bash
uv run python -m shepherd_pipeline.cli models
```

## Usage Examples

### Example 1: Process YouTube Video with Time Range

Process a specific segment of a YouTube video (27:30 to 1:19:20):

```bash
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=3TeBv1lXLHA" \
  --start 1650 \
  --end 4760 \
  --transcription-model voxtral-mini-latest
```

### Example 2: Use OpenAI for Summarization

Mix providers - use Mistral for transcription and OpenAI for summarization:

```bash
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=3TeBv1lXLHA" \
  --start 1650 \
  --end 4760 \
  --summary-model gpt-4o-mini \
```

### Example 3: Mock Mode for Testing

Test the pipeline without making real API calls:

```bash
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --mock
```

### Example 4: Custom Summary Instructions

Provide specific instructions for the summarization:

```bash
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --summary-instruction "請提供詳細的內容摘要，重點關注講道的主要信息和聖經教導" \
  --summary-word-count 2000 \
  --lang zh-TW
```

### OpenAI Models

**Text Processing Only (no transcription):**
- `gpt-3.5-turbo`: Fast and cost-effective
- `gpt-4o-mini`: Balanced performance
- `gpt-4o`: High quality
- `gpt-4`: Highest quality
- `gpt-4-turbo`: Fast GPT-4 variant

## Tips and Best Practices

1. **Time Range Selection**: Use `--start` and `--end` for processing specific segments of long videos
2. **Model Selection**: Use Mistral models for Chinese content, OpenAI for English
3. **Chunk Size**: Smaller chunks (5-10 minutes) provide better accuracy but take longer
4. **Export Paths**: Use `{timestamp}` placeholder to avoid overwriting files
5. **Mock Mode**: Always test with `--mock` first to verify your command works

## Environment Variables

The CLI respects these environment variables:
- `MISTRAL_API_KEY`: Required for Mistral models in production
- `OPENAI_API_KEY`: Required for OpenAI models in production
- Configuration managed through `.env` file and settings.py

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `.env` file contains valid API keys
2. **Model Not Found**: Use `uv run python -m shepherd_pipeline.cli models` to see available models
3. **Time Range Errors**: Ensure `--end` is greater than `--start`
4. **Export Path Errors**: Ensure the parent directory exists or will be created

### Debug Mode

For detailed logging, set the environment variable:
```bash
export PREFECT_LOG_LEVEL=DEBUG
```
