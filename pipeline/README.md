# Shepherd Pipeline

A Prefect-powered AI transcription and summarization system focused on YouTube video processing with multi-provider AI support, Chinese language processing, and production-ready workflows.

## Current Implementation

**YouTube Video Pipeline (Production Ready)**:
1. **Video Download** → yt-dlp with precise time range extraction
2. **Audio Processing** → Chunking and format conversion
3. **AI Transcription** → Multi-provider support (Voxtral, OpenAI)
4. **Chinese Translation** → Traditional Chinese conversion with OpenCC
5. **AI Text Correction** → Context-aware correction for Christian content
6. **AI Summarization** → Configurable summarization with custom instructions

**Key Features**:
- **Multi-Provider AI**: Runtime model selection across OpenAI and Mistral providers
- **Chinese Language Processing**: Specialized Traditional Chinese (Taiwan) processing
- **Artifact Caching**: Intelligent caching with content deduplication and pipeline resumption
- **Mock-First Development**: Comprehensive mock APIs for local development
- **Type-Safe Workflows**: Full type validation with Pydantic schemas
- **Professional CLI**: Rich command-line interface with export capabilities

## Quick Start

### Prerequisites

**Python 3.12** and **uv** package manager are required. For detailed installation instructions, see [Python Environment Setup](llm-docs/python-env.md).

**Quick Install**:
```bash
# Install pyenv and Python 3.12
brew install pyenv  # macOS
pyenv install 3.12 && pyenv local 3.12

# Install uv
pip install uv
```

### Setup and Run

```bash
# Install dependencies
uv sync

# Set up pre-commit hooks
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Copy environment file
cp .env.example .env

# Start Prefect server (optional - demo works without it)
docker compose up -d

# Run CLI commands
uv run python -m shepherd_pipeline.cli --help

# Process YouTube video with time range
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=3TeBv1lXLHA" \
  --start 1650 --end 4760 \
  --export-transcript exports/transcript-{timestamp}.txt \
  --export-summary exports/summary-{timestamp}.txt

# Use mock mode for testing
uv run python -m shepherd_pipeline.cli youtube \
  "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --mock
```

## Project Structure

```
shepherd_pipeline/
├── flows/           # Prefect flow definitions
├── tasks/           # Individual Prefect tasks
├── models/          # Pydantic models and schemas
├── services/        # External service integrations (mocked)
├── config/          # Configuration management
└── cli/             # Command-line interface
```

## Development

**Documentation Structure**:
- **[Python Environment Setup](llm-docs/python-env.md)** - pyenv and uv installation
- **[Local Development Setup](llm-docs/local-dev.md)** - Docker infrastructure and project configuration
- **[CLI Usage Guide](llm-docs/cli-usage.md)** - Command-line interface documentation
- **[Code Quality Guide](llm-docs/code-quality.md)** - Development tools and workflows

For complete development documentation, see [llm-docs/](llm-docs/) directory or refer to [llms.txt](llms.txt) for structured project overview.
