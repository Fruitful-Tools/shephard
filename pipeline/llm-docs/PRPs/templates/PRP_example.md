## FEATURE:

Implement a new Chinese text summarization pipeline with configurable AI models and Traditional Chinese output optimization for Christian content processing in the Shepherd Pipeline system.

## EXAMPLES:

**YouTube Pipeline Example** (see shepherd_pipeline/flows/main_flows.py):
- Input: YouTube URL with time range (youtube_start_time, youtube_end_time)
- Process: Download → Audio extraction → Chunking → Transcription → Chinese translation → AI correction → Summarization
- Output: PipelineResult with comprehensive metadata and processing results

**CLI Usage Example**:
```bash
# Process YouTube video with mock services
uv run python -m shepherd_pipeline.cli youtube \
  --url "https://youtube.com/watch?v=example" \
  --start-time "00:05:30" \
  --end-time "00:15:45" \
  --model mistral-small-latest \
  --mock

# Real API processing
uv run python -m shepherd_pipeline.cli youtube \
  --url "https://youtube.com/watch?v=example" \
  --model gpt-4o-mini \
  --output-file "summary_{timestamp}.md"
```

**Model Configuration Example** (see shepherd_pipeline/config/settings.py):
```python
class Settings(BaseSettings):
    transcription_model: str = Field(default="voxtral-mini-latest")
    correction_model: str = Field(default="mistral-small-latest")
    summarization_model: str = Field(default="gpt-4o-mini")
    use_mocks: bool = Field(default=False)
```

## DOCUMENTATION:

**Essential Shepherd Pipeline Documentation:**
- llms.txt: Primary project overview and architecture
- CLAUDE.md: Development workflow and essential commands
- llm-docs/project-spec.md: Architectural blueprint and implementation status
- llm-docs/model-configuration.md: Multi-provider AI model patterns
- llm-docs/chinese-translation.md: OpenCC Traditional Chinese processing
- llm-docs/artifact-system.md: SHA-256 deduplication and caching
- llm-docs/logging.md: Hybrid Prefect + Loguru logging approach

**External Documentation:**
- Prefect 3.0+ Documentation: https://docs.prefect.io/ (async flow patterns, task retries)
- Pydantic v2 Documentation: https://docs.pydantic.dev/latest/ (model validation, ConfigDict)
- uv Documentation: https://docs.astral.sh/uv/ (dependency management, virtual environments)
- OpenCC Documentation: https://github.com/BYVoid/OpenCC (Chinese text conversion)
- yt-dlp Documentation: https://github.com/yt-dlp/yt-dlp (YouTube download patterns)

**AI Service Documentation:**
- Mistral API: https://docs.mistral.ai/ (text correction, summarization)
- OpenAI API: https://platform.openai.com/docs/ (premium text processing)
- Voxtral API: Uses Mistral API key for audio transcription

## OTHER CONSIDERATIONS:

**Shepherd Pipeline Specific Gotchas:**

1. **Prefect 3.0+ Patterns**: All flows must be async, use @task and @flow decorators properly, always use get_run_logger() not standard logging

2. **Mock-First Development**: Every external service MUST have a mock implementation in services/mock_apis.py, controlled by --mock flag and USE_MOCKS setting

3. **Pydantic v2 Migration**: Use ConfigDict not Config class, Field(...) for validation, model_validator for complex validation

4. **uv Dependency Management**: Always use 'uv sync' not 'pip install', 'uv run' for all commands, dependencies in pyproject.toml

5. **Chinese Language Processing**: Use OpenCC for Traditional Chinese conversion, follow patterns in translation_service.py for Christian content optimization

6. **Artifact Management**: Implement SHA-256 content deduplication, use artifact_manager.py patterns, cleanup in flow-level try/finally blocks

7. **Error Handling**: Return PipelineResult with success/error status, comprehensive error messages, processing metadata

8. **CLI Integration**: Follow existing youtube/models command patterns, use click decorators, rich terminal output

9. **Configuration**: Environment-based settings with Pydantic Settings, runtime model selection through PipelineInput

10. **Testing**: Use Prefect test harness, pytest fixtures from conftest.py, separate unit/integration tests, relaxed MyPy rules for test files

**Common AI Assistant Mistakes to Avoid:**
- Don't use sync functions in async Prefect flows
- Don't forget to add mock implementations for new services
- Don't skip input validation with Pydantic models
- Don't use standard logging instead of get_run_logger()
- Don't create new patterns when existing ones work
- Don't ignore the --mock flag for development
- Don't forget to update llms.txt when adding new components
