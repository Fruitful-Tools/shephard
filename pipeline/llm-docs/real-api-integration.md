# Real API Integration Guide

This guide covers the implementation and usage of real external API services in the Shepherd Pipeline, including Voxtral transcription, Mistral text processing, and OpenAI language models. The system provides seamless switching between mock and production APIs.

## Architecture Overview

### Service Layer Design

The pipeline uses a three-tier architecture for API integration:

1. **Service Layer**: Direct API client implementations
2. **Factory Layer**: Dynamic service instantiation based on configuration
3. **Task Layer**: Prefect tasks that orchestrate service calls

```python
# Service instantiation flow
ModelFactory → OpenAIService/MistralService → HTTP API calls
```

### Mock vs Production Switching

API mode controlled via CLI flags and configuration settings:

```python
# Development mode (uses mocks) - via CLI
--mock

# Production mode (uses real APIs) - default
# Controlled by settings.is_development and CLI flags
```

## Voxtral Transcription Service

### Service Implementation

The Voxtral service provides audio-to-text transcription through Mistral's API:

```python
from shepherd_pipeline.services.voxtral_service import VoxtralService

service = VoxtralService()
result = await service.transcribe_chunk(
    audio_chunk_path="/path/to/audio.mp3",
    language="zh",  # Chinese language code
    model="voxtral-mini-latest"
)
```

### API Configuration

**Endpoint**: `https://api.mistral.ai/v1/audio/transcriptions`

**Authentication**: Bearer token using `MISTRAL_API_KEY`

**Request Format**:
```python
files = {'file': open(audio_path, 'rb')}
data = {
    'model': 'voxtral-mini-latest',
    'language': 'zh',
    'response_format': 'verbose_json'  # Include timestamps
}
headers = {'Authorization': f'Bearer {api_key}'}
```

### Response Processing

The service processes Voxtral API responses to extract:

```python
# Extract transcription components
transcription_text = result.get('text', '').strip()
confidence = result.get('confidence', 0.95)

# Process timestamps
timestamps = []
if 'segments' in result:
    for segment in result['segments']:
        timestamps.append({
            'start': segment.get('start', 0.0),
            'end': segment.get('end', 0.0),
            'text': segment.get('text', '').strip()
        })
```

### Error Handling

Comprehensive error handling with fallback responses:

```python
try:
    response = requests.post(url, headers=headers, files=files, data=data, timeout=120.0)
    response.raise_for_status()
    return process_successful_response(response.json())

except FileNotFoundError:
    return TranscriptionResult(
        chunk_id=chunk_id,
        raw_text="[音頻文件未找到]",
        confidence=0.0,
        language=language,
        timestamps=[]
    )
except requests.exceptions.RequestException as e:
    logger.error(f"Voxtral API request failed: {e}")
    return fallback_response()
```

## Mistral Text Processing Service

### Service Architecture

The Mistral service handles both text correction and summarization:

```python
from shepherd_pipeline.services.mistral_service import MistralService

service = MistralService()

# Text correction
correction = await service.correct_text(
    text="原始transcription文字",
    target_language="zh-TW",
    model="mistral-small-latest"
)

# Text summarization
summary = await service.summarize_text(
    text="完整文本內容",
    instructions="請重點關注基督教信息",
    word_limit=100,
    model="mistral-small-latest"
)
```

### API Configuration

**Endpoint**: `https://api.mistral.ai/v1/chat/completions`

**Authentication**: Bearer token using `MISTRAL_API_KEY`

**Request Format**:
```python
payload = {
    "model": "mistral-small-latest",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ],
    "temperature": 0.1,  # Low for correction, higher for summarization
    "max_tokens": 2000
}
```

### Christian Context Prompting

Specialized prompts for Christian content processing:

```python
correction_prompt = """這是一段audio transcription，因為是AI產生了，可能有許多錯字與問題，我需要你把它轉成正確的格式，注意這是基督教的文章或者講道或者見證，所以當你不太確定用語的時候，可以朝這個方向思考。

請修正以下內容：
1. 修正錯字和語法錯誤
2. 使用繁體中文（台灣）
3. 適當的標點符號
4. 保持基督教用語的準確性
5. 確保語句通順自然

只回傳修正後的文字，不要額外說明。"""

summarization_prompt = """請為這段基督教內容製作摘要，重點包括：
1. 主要的屬靈教導或信息
2. 重要的聖經引用或原則
3. 實際的應用或呼籲
4. 見證或例子的核心要點

請用繁體中文（台灣）回應，保持基督教用語的準確性。"""
```

### Response Processing

Extract and validate API responses:

```python
try:
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()

        result = response.json()
        processed_text = result["choices"][0]["message"]["content"].strip()

        return CorrectionResult(
            chunk_id="mistral_corrected",
            original_text=text,
            corrected_text=processed_text,
            language=target_language,
            model_used=model
        )
except Exception as e:
    logger.error(f"Mistral API failed: {e}")
    return fallback_result()
```

## OpenAI Language Model Service

### Service Implementation

OpenAI service provides high-quality text processing:

```python
from shepherd_pipeline.services.openai_service import OpenAIService

service = OpenAIService()

# Text correction using GPT-4
correction = await service.correct_text(
    text="需要修正的文字",
    target_language="zh-TW",
    model="gpt-4o-mini"
)

# Summarization using GPT models
summary = await service.summarize_text(
    text="完整內容",
    instructions="客製化指示",
    word_limit=150,
    model="gpt-4o"
)
```

### API Configuration

**Endpoint**: `https://api.openai.com/v1/chat/completions`

**Authentication**: Bearer token using `OPENAI_API_KEY`

**Model Selection**:
- `gpt-4o-mini`: Cost-effective, high-quality
- `gpt-4o`: Premium performance
- `gpt-4`: Legacy premium model
- `gpt-3.5-turbo`: Budget option

### Request Optimization

Optimized requests for Chinese text processing:

```python
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": chinese_system_prompt},
        {"role": "user", "content": text}
    ],
    "temperature": 0.1,  # Deterministic for correction
    "max_tokens": word_limit * 2 if word_limit else 1000  # Dynamic token limit
}
```

## Model Factory Integration

### Dynamic Service Selection

The model factory enables runtime service selection:

```python
from shepherd_pipeline.services.model_factory import ModelFactory

# Automatic provider detection
text_processor = ModelFactory.create_text_processor(
    model="gpt-4o-mini",  # Automatically routes to OpenAI
    use_mock=False
)

summarizer = ModelFactory.create_summarization_service(
    model="mistral-small-latest",  # Automatically routes to Mistral
    use_mock=False
)
```

### Provider Mapping

Model-to-provider associations:

```python
MODEL_PROVIDERS = {
    # OpenAI models
    "gpt-4": AIProvider.OPENAI,
    "gpt-4o": AIProvider.OPENAI,
    "gpt-4o-mini": AIProvider.OPENAI,
    "gpt-3.5-turbo": AIProvider.OPENAI,

    # Mistral models
    "mistral-small-latest": AIProvider.MISTRAL,
    "mistral-medium": AIProvider.MISTRAL,
    "mistral-medium-2505": AIProvider.MISTRAL,
    "voxtral-mini-latest": AIProvider.MISTRAL,
    "voxtral-mini-latest": AIProvider.MISTRAL,
}
```

## Environment Configuration

### API Key Management

Configure API keys through environment variables:

```bash
# Environment or .env file
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Override default models in settings
CORRECTION_MODEL=gpt-4o-mini
SUMMARIZATION_MODEL=mistral-small-latest
```

### Settings Validation

The settings class validates configuration:

```python
class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = Field(default="mock_openai_key")
    mistral_api_key: str = Field(default="mock_mistral_key")

    # Model Configuration
    supported_correction_models: list[str] = Field(default=[
        "mistral-small-latest", "mistral-medium", "mistral-medium-2505",
        "gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"
    ])
```

## Task Integration

### Transcription Task

The transcription task integrates Voxtral with Chinese translation:

```python
@task(retries=2, retry_delay_seconds=10)
async def transcribe_audio_chunk(
    audio_chunk: AudioChunk,
    model: str = "voxtral-mini-latest",
    language: str = "zh-TW"
) -> TranscriptionResult:
    if settings.is_development:
        # Use mock service
        voxtral_service = MockVoxtralService()
        result = await voxtral_service.transcribe_chunk(audio_chunk.file_path, language)
    else:
        # Use real Voxtral API
        real_voxtral_service = VoxtralService()
        voxtral_language = "zh" if language.startswith("zh") else language
        result = await real_voxtral_service.transcribe_chunk(
            audio_chunk.file_path, voxtral_language, model
        )

    # Apply Chinese translation
    translation_service = ChineseTranslationService()
    translated_text = translation_service.to_traditional_chinese(result.raw_text)
    result.raw_text = translated_text
    result.language = language

    return result
```

### Text Processing Tasks

Text correction and summarization use the model factory:

```python
@task(retries=2, retry_delay_seconds=5)
async def correct_transcription(
    transcription: TranscriptionResult,
    target_language: str = "zh-TW",
    model: str = "mistral-small-latest"
) -> CorrectionResult:
    # Dynamic service selection
    text_processor = ModelFactory.create_text_processor(
        model=model, use_mock=settings.is_development
    )

    result = await text_processor.correct_text(
        transcription.raw_text, target_language, model
    )
    result.chunk_id = transcription.chunk_id
    return result
```

## Performance and Rate Limiting

### API Rate Limits

Understanding provider rate limits:

| Provider | Model | Requests/min | Tokens/min |
|----------|-------|--------------|------------|
| OpenAI | gpt-4o-mini | 500 | 200,000 |
| OpenAI | gpt-4o | 100 | 30,000 |
| Mistral | mistral-small-latest | 100 | 1,000,000 |
| Mistral | Voxtral | 20 | N/A (audio) |

### Retry Strategies

Prefect tasks include retry logic:

```python
@task(retries=2, retry_delay_seconds=10)
async def api_task():
    # Task automatically retries on failure
    # Exponential backoff handled by Prefect
    pass
```

### Timeout Configuration

Appropriate timeouts for different operations:

```python
# Voxtral transcription (audio processing)
timeout = 120.0  # 2 minutes

# Text correction (fast)
timeout = 30.0   # 30 seconds

# Summarization (may be longer)
timeout = 45.0   # 45 seconds
```

## Error Handling and Monitoring

### Comprehensive Error Handling

All services implement fallback strategies:

```python
try:
    # Attempt API call
    response = await api_call()
    return process_success(response)

except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error {e.response.status_code}: {e}")
    return fallback_response()

except httpx.TimeoutException:
    logger.error("API timeout exceeded")
    return timeout_fallback()

except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return generic_fallback()
```

### Logging and Observability

Structured logging for API interactions:

```python
# Log API calls
logger.info(f"Calling {provider} API with model {model}")
logger.info(f"Input length: {len(text)} characters")

# Log results
logger.info(f"API response received: {len(result)} characters")
logger.info(f"Processing time: {duration:.2f}s")

# Log errors
logger.error(f"API call failed: {error}")
logger.error(f"Fallback strategy used: {fallback_type}")
```

### Health Checks

Validate API connectivity:

```python
async def health_check_apis():
    """Check API health and connectivity."""
    results = {}

    # Test Mistral API
    try:
        service = MistralService()
        test_result = await service.correct_text("test", "zh-TW", "mistral-small-latest")
        results["mistral"] = "healthy"
    except Exception as e:
        results["mistral"] = f"error: {e}"

    # Test OpenAI API
    try:
        service = OpenAIService()
        test_result = await service.correct_text("test", "zh-TW", "gpt-4o-mini")
        results["openai"] = "healthy"
    except Exception as e:
        results["openai"] = f"error: {e}"

    return results
```

## Cost Optimization

### Model Selection for Cost Efficiency

Choose models based on use case:

```python
# Cost-effective configuration
BUDGET_MODELS = {
    "correction": "mistral-small-latest",      # $0.2/1M tokens
    "summarization": "gpt-4o-mini"     # $0.15/1M tokens
}

# Premium quality configuration
PREMIUM_MODELS = {
    "correction": "gpt-4o",            # $2.5/1M tokens
    "summarization": "gpt-4"           # $30/1M tokens
}
```

### Batch Processing

Optimize for batch operations:

```python
# Process multiple chunks efficiently
async def process_batch(chunks: list[AudioChunk]):
    # Use cost-effective model for large batches
    model = "mistral-small-latest" if len(chunks) > 10 else "gpt-4o-mini"

    tasks = []
    for chunk in chunks:
        task = correct_transcription.submit(chunk, model=model)
        tasks.append(task)

    return await gather_results(tasks)
```

## Testing Real APIs

### Integration Testing

Test real API integration:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_mistral_correction():
    """Test real Mistral API correction."""
    if not os.getenv("MISTRAL_API_KEY"):
        pytest.skip("MISTRAL_API_KEY not set")

    service = MistralService()
    result = await service.correct_text(
        "测试文字", "zh-TW", "mistral-small-latest"
    )

    assert result.corrected_text != "测试文字"
    assert result.model_used == "mistral-small-latest"
```

### Mock vs Real Comparison

Validate mock accuracy against real APIs:

```python
async def compare_mock_vs_real():
    """Compare mock and real API responses."""
    text = "基督教信仰见证"

    # Mock result
    mock_service = MockMistralService()
    mock_result = await mock_service.correct_text(text, "zh-TW")

    # Real result
    real_service = MistralService()
    real_result = await real_service.correct_text(text, "zh-TW")

    # Compare characteristics
    assert len(mock_result.corrected_text) > 0
    assert len(real_result.corrected_text) > 0
    assert mock_result.language == real_result.language
```

## Best Practices

### API Key Security

1. **Environment Variables**: Store keys in `.env`, never in code
2. **Key Rotation**: Regularly rotate API keys
3. **Access Control**: Limit key permissions where possible
4. **Monitoring**: Monitor API usage for unusual patterns

### Error Recovery

1. **Graceful Degradation**: Always provide fallback responses
2. **Retry Logic**: Implement exponential backoff
3. **Circuit Breakers**: Prevent cascade failures
4. **User Communication**: Inform users of service issues

### Performance Optimization

1. **Model Selection**: Choose appropriate models for use case
2. **Batch Processing**: Group requests where possible
3. **Caching**: Cache results for repeated inputs
4. **Monitoring**: Track API response times and errors

### Cost Management

1. **Usage Tracking**: Monitor token consumption
2. **Budget Alerts**: Set up cost monitoring
3. **Model Optimization**: Use cost-effective models where quality permits
4. **Batch Efficiency**: Optimize request patterns

This comprehensive real API integration provides robust, production-ready AI services while maintaining flexibility and cost efficiency.
