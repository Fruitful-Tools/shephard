# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Entry Point

**Always start with `llms.txt`** - This is the preferred entry point for understanding the project structure, locating files, and understanding the architecture. The llms.txt file provides a structured overview of all key components.

## Essential Commands

### Development Setup
```bash
# Initial setup
uv sync
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
cp .env.example .env
docker compose up -d

# Daily development
uv run python -m shepard_pipeline.demo  # Run demo pipeline
open http://localhost:4200              # Access Prefect UI
```

### Code Quality (Systematic Workflow)
```bash
# ALWAYS follow this order for pre-commit fixes:
git add -A                      # Stage files first (required)
uv run ruff format .           # Format code
uv run ruff check --fix .      # Fix linting issues
uv run mypy .                  # Type checking
uv run pre-commit run --all-files  # Final validation

# Commit with conventional format
git commit -m "feat: add new feature"  # Manual commit
uv run cz commit                       # Interactive commit helper
```

### Testing
```bash
uv run pytest                     # All tests
uv run pytest tests/unit/         # Unit tests only
uv run pytest tests/integration/  # Integration tests only
uv run pytest tests/unit/test_models.py::TestPipelineResult  # Specific test
uv run pytest -v -s              # Verbose output with prints
```

### Infrastructure
```bash
docker compose up -d              # Start Prefect server + PostgreSQL
docker compose logs -f prefect-server  # View logs
docker compose down               # Stop infrastructure
```

## Architecture Overview

### Core Flow Pattern
The system uses a **dispatcher → specialized flow** pattern:
- `main_pipeline_flow()` routes requests based on `EntryPointType` (YOUTUBE, AUDIO_FILE, TEXT)
- Each specialized flow (`youtube_pipeline_flow`, `audio_file_pipeline_flow`, `text_summary_pipeline_flow`) handles specific processing chains
- All flows return `PipelineResult` with consistent metadata and error handling

### Data Flow Architecture
```
PipelineInput (validated) → Flow Router → Specialized Flow → Atomic Tasks → PipelineResult
```

**Key Data Models:**
- `PipelineInput`: Entry point with discriminator fields for different input types
- `PipelineResult`: Comprehensive output with status, metadata, processing results, and error details
- Task-specific models: `AudioChunk`, `TranscriptionResult`, `CorrectionResult`, `SummaryResult`

### Mock-First Development
- All external APIs are mocked in `services/mock_apis.py`
- Controlled by `MOCK_EXTERNAL_APIS=true` environment variable
- Mock services provide realistic data and behavior for development

### Task Design Principles
- Each processing step is an independent Prefect `@task` with retries
- Tasks are atomic and stateless - can be retried safely
- Error handling at task level with proper logging via `get_run_logger()`
- Temporary file cleanup handled in flow-level try/finally blocks

## Configuration System

### Environment-Based Settings
Configuration managed through `config/settings.py` using Pydantic Settings:
- Development vs production mode switching
- Model selection for AI services (Voxtral, OpenAI, Mistral)
- Processing parameters (chunk sizes, timeouts, rate limits)
- Database and external service credentials

### Runtime Configuration
Pipeline parameters configured per-job through `PipelineInput`:
- Model selection at runtime (transcription and summarization models)
- Custom processing instructions and prompts
- Language settings and output formatting
- Resource limits and timeout configurations

## Testing Strategy

### Integration Tests (`tests/integration/`)
- Test complete pipeline flows end-to-end
- Use Prefect test harness for flow execution
- Mock all external services via environment variables
- Validate full data flow from input to result

### Unit Tests (`tests/unit/`)
- Test individual models, services, and utilities
- Use pytest fixtures from `tests/conftest.py`
- Focus on business logic, validation, and error cases
- Mock external dependencies at service level

### Test Configuration
- MyPy rules relaxed for test files (no untyped decorator warnings)
- Pytest markers: `slow`, `integration`, `unit` for selective test running
- Test data fixtures provide realistic sample inputs and expected outputs

## Development Workflow Integration

### Context7 Usage
When developing, use Context7 (https://context7.com) to fetch latest best practices for:
- Prefect 3.0+ patterns and async flow design
- uv dependency management and environment setup
- mypy configuration and type annotation standards
- Ruff linting rules and modern Python syntax
- pytest testing patterns and fixture design

### Documentation Maintenance
1. Update relevant docs in `llm-docs/` when making architectural changes
2. Update `llms.txt` entries for new files or changed functionality
3. Maintain documentation accuracy reflecting current implementation

## Key File Relationships

- **Flows** (`flows/main_flows.py`) orchestrate tasks and handle errors
- **Tasks** (`tasks/`) are atomic, retryable operations
- **Models** (`models/pipeline.py`) define data contracts and validation
- **Services** (`services/mock_apis.py`) abstract external API interactions
- **Config** (`config/settings.py`) centralizes environment-based configuration
