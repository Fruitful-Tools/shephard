# Model Configuration and Selection

The Shepherd Pipeline supports flexible AI model selection across multiple providers (OpenAI, Mistral) with runtime switching capabilities. This document covers model configuration, selection patterns, and integration architecture.

## Architecture Overview

### Model Factory Pattern

The pipeline uses a factory pattern to abstract model selection and service instantiation:

```python
from shepherd_pipeline.services.model_factory import ModelFactory

# Create appropriate service based on model
text_processor = ModelFactory.create_text_processor(
    model="gpt-4o-mini",
    use_mock=False
)

# Automatically routes to OpenAI service
result = await text_processor.correct_text(text, "zh-TW", "gpt-4o-mini")
```

### Supported Providers

| Provider | Models | Use Cases |
|----------|--------|-----------|
| **OpenAI** | `gpt-4`, `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`, `gpt-4-turbo` | High-quality text correction and summarization |
| **Mistral** | `mistral-small-latest`, `mistral-medium`, `mistral-medium-2505`, `mistral-large`, `voxtral-mini-latest` | Cost-effective processing, specialized audio models |
| **Mock** | `mock-model` | Development and testing |

## Configuration Management

### Environment Variables

Configure model selection through environment variables or runtime parameters:

```bash
# .env configuration
CORRECTION_MODEL=gpt-4o-mini
SUMMARIZATION_MODEL=mistral-small-latest
MOCK_EXTERNAL_APIS=false
OPENAI_API_KEY=your_openai_key
MISTRAL_API_KEY=your_mistral_key
```

### Runtime Model Selection

Models can be selected per job through `PipelineInput`:

```python
from shepherd_pipeline.models.pipeline import PipelineInput, EntryPointType

pipeline_input = PipelineInput(
    text_content="Text to process...",
    correction_model="gpt-4o-mini",        # Use OpenAI for correction
    summarization_model="mistral-small-latest",   # Use Mistral for summary
    target_language="zh-TW"
)
```

### Configuration Validation

The system validates model compatibility and availability:

```python
from shepherd_pipeline.services.model_factory import ModelFactory

# Validate model support
is_valid = ModelFactory.validate_model("gpt-4o-mini")  # True

# Get supported models by provider
models = ModelFactory.get_supported_models()
# {
#   AIProvider.OPENAI: ["gpt-4", "gpt-4o", "gpt-4o-mini", ...],
#   AIProvider.MISTRAL: ["mistral-small-latest", "mistral-medium", ...],
#   AIProvider.MOCK: ["mock-model"]
# }
```

## Model Selection Strategies

### Cost Optimization

Balance cost and quality based on use case:

```python
# Cost-effective configuration
BUDGET_CONFIG = {
    "correction_model": "mistral-small-latest",      # Lower cost
    "summarization_model": "gpt-4o-mini",    # Good quality/cost ratio
}

# High-quality configuration
PREMIUM_CONFIG = {
    "correction_model": "gpt-4o",           # Best quality
    "summarization_model": "gpt-4",         # Premium performance
}
```

### Language-Specific Optimization

Optimize for Chinese language processing:

```python
# Traditional Chinese optimization
CHINESE_CONFIG = {
    "correction_model": "gpt-4o-mini",        # Excellent Chinese support
    "summarization_model": "mistral-small-latest",   # Cost-effective Chinese processing
    "target_language": "zh-TW"               # Taiwan Traditional Chinese
}
```

### Christian Content Specialization

Both OpenAI and Mistral services include Christian-context prompts:

```python
# Christian content processing
christian_prompt = '''這是基督教的文章或者講道或者見證，所以當你不太確定用語的時候，可以朝這個方向思考。

請修正以下內容：
1. 修正錯字和語法錯誤
2. 使用繁體中文（台灣）
3. 適當的標點符號
4. 保持基督教用語的準確性
5. 確保語句通順自然'''
```

## Task-Level Integration

### Text Correction Task

The `correct_transcription` task automatically selects the appropriate service:

```python
@task(retries=2, retry_delay_seconds=5)
async def correct_transcription(
    transcription: TranscriptionResult,
    target_language: str = "zh-TW",
    model: str = "mistral-small-latest"
) -> CorrectionResult:
    # Model factory handles provider selection
    text_processor = ModelFactory.create_text_processor(
        model=model, use_mock=settings.is_development
    )

    result = await text_processor.correct_text(
        transcription.raw_text, target_language, model
    )
    result.chunk_id = transcription.chunk_id
    return result
```

### Summarization Task

The `summarize_text` task supports both providers seamlessly:

```python
@task(retries=2, retry_delay_seconds=10)
async def summarize_text(
    text: str,
    instructions: str | None = None,
    word_limit: int | None = None,
    model: str = "mistral-small-latest"
) -> SummaryResult:
    # Automatic service selection based on model
    summarizer = ModelFactory.create_summarization_service(
        model=model, use_mock=settings.is_development
    )

    return await summarizer.summarize_text(
        text=text, instructions=instructions,
        word_limit=word_limit, model=model
    )
```

## Error Handling and Fallbacks

### API Failure Handling

Both services implement graceful degradation:

```python
try:
    # Attempt API call
    result = await service.correct_text(text, "zh-TW", model)
except Exception as e:
    logger.error(f"API correction failed: {e}")
    # Return original text as fallback
    return CorrectionResult(
        chunk_id="fallback",
        original_text=text,
        corrected_text=text,  # Fallback to original
        language="zh-TW",
        model_used=f"{model}_failed"
    )
```

### Mock Service Switching

Seamless development/production switching:

```python
# Development mode (uses mocks)
settings.mock_external_apis = True
processor = ModelFactory.create_text_processor("gpt-4o-mini", use_mock=True)
# Returns MockMistralService instance

# Production mode (uses real APIs)
settings.mock_external_apis = False
processor = ModelFactory.create_text_processor("gpt-4o-mini", use_mock=False)
# Returns OpenAIService instance
```

## Performance Considerations

### Model Performance Characteristics

| Model | Speed | Quality | Cost | Chinese Support |
|-------|--------|---------|------|----------------|
| `gpt-4o-mini` | Fast | High | Low | Excellent |
| `gpt-4o` | Medium | Highest | High | Excellent |
| `mistral-small-latest` | Fast | Good | Low | Good |
| `mistral-medium` | Medium | High | Medium | Good |

### Batch Processing Optimization

For large-scale processing, consider model selection based on volume:

```python
# High-volume processing
if batch_size > 100:
    model = "mistral-small-latest"  # Cost-effective for large batches
else:
    model = "gpt-4o-mini"    # Higher quality for smaller batches
```

## Testing and Validation

### Model Factory Testing

```python
def test_model_routing():
    # Test OpenAI routing
    processor = ModelFactory.create_text_processor("gpt-4o-mini", use_mock=False)
    assert isinstance(processor, OpenAIService)

    # Test Mistral routing
    processor = ModelFactory.create_text_processor("mistral-small-latest", use_mock=False)
    assert isinstance(processor, MistralService)

    # Test mock routing
    processor = ModelFactory.create_text_processor("any-model", use_mock=True)
    assert isinstance(processor, MockMistralService)
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_cross_model_pipeline():
    # Test mixed provider pipeline
    result = await correct_transcription(
        transcription, target_language="zh-TW", model="gpt-4o-mini"  # OpenAI
    )

    summary = await summarize_text(
        result.corrected_text, model="mistral-small-latest"  # Mistral
    )

    assert result.model_used == "gpt-4o-mini"
    assert summary.model_used == "mistral-small-latest"
```

## Best Practices

### Model Selection Guidelines

1. **Development**: Always use mock services (`MOCK_EXTERNAL_APIS=true`)
2. **Testing**: Test with multiple model combinations
3. **Production**: Choose models based on quality/cost requirements
4. **Chinese Content**: Prefer `gpt-4o-mini` for accuracy, `mistral-small-latest` for cost
5. **Error Handling**: Always implement fallback strategies

### Configuration Management

1. Use environment variables for global defaults
2. Override per-job through `PipelineInput`
3. Validate model availability before processing
4. Log model selection decisions for debugging

### Monitoring and Observability

```python
# Log model selection decisions
logger.info(f"Using {model} via {provider} for text correction")
logger.info(f"Processing {len(text)} characters with {model}")

# Track model performance metrics
metrics = {
    "model": model,
    "provider": provider,
    "processing_time": duration,
    "input_length": len(text),
    "output_length": len(result)
}
```

## Migration Guide

### From Single Provider to Multi-Provider

1. **Update imports**:
   ```python
   # Old
   from ..services.mistral_service import MistralService

   # New
   from ..services.model_factory import ModelFactory
   ```

2. **Update service instantiation**:
   ```python
   # Old
   service = MistralService()

   # New
   service = ModelFactory.create_text_processor(model, use_mock=False)
   ```

3. **Update configuration**:
   ```python
   # Add to settings.py
   supported_correction_models: list[str] = [
       "mistral-small-latest", "gpt-4o-mini", "gpt-4o"
   ]
   ```

4. **Test migration**:
   ```bash
   # Test with different models
   uv run pytest tests/unit/test_model_factory.py -v
   ```

This flexible model selection system enables cost optimization, quality tuning, and seamless provider switching while maintaining a consistent interface across the pipeline.
