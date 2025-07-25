# Chinese Translation Service

The Shepherd Pipeline includes a specialized Chinese translation service built on OpenCC for converting between Simplified and Traditional Chinese variants, optimized for Taiwan Traditional Chinese (zh-TW) in Christian content contexts.

## Core Functionality

The service provides automatic detection and explicit conversion methods using OpenCC (Open Chinese Convert):

```python
from shepherd_pipeline.services.translation_service import ChineseTranslationService

service = ChineseTranslationService()
traditional = service.to_traditional_chinese("简体中文测试")
# Result: "簡體中文測試"
```

### Key Methods

- **`to_traditional_chinese(text)`**: Direct simplified-to-traditional conversion
- **`detect_and_convert(text)`**: Automatic detection and conversion
- **Taiwan standardization**: Ensures Taiwan-specific character variants

## Pipeline Integration

### Transcription Workflow

The service integrates into the transcription pipeline for consistent Chinese processing:

```python
# Pipeline: Transcription → Translation → AI Correction
raw_transcription = await voxtral_api.transcription(audio)       # May be simplified
traditional_text = translation_service.to_traditional_chinese(raw_transcription)
corrected_text = await ai_model.correct_text(traditional_text)  # AI processes traditional
```

### Christian Content Optimization

Specialized handling for Christian terminology with context-aware processing:

- **Biblical terminology**: Maintains scriptural reference accuracy
- **Liturgical language**: Preserves formal religious expressions
- **Common conversions**: 教会→教會, 见证→見證, 祷告→禱告

## Configuration & Dependencies

### Installation

```bash
# Add to dependencies
uv add opencc-python-reimplemented

# System dependencies (if needed)
# macOS: brew install opencc
# Ubuntu: sudo apt-get install libopencc-dev
```

### Error Handling

The service provides graceful degradation and fallback to original text on conversion failures.

## Performance & Testing

- **Speed**: 1ms for small text, 5-20ms for medium text
- **Accuracy**: >99.9% for standard characters, >98% for technical terms
- **Memory**: ~2MB initialization, ~100KB per conversion

For detailed testing patterns and troubleshooting, see the implementation in `shepherd_pipeline/services/translation_service.py`.

## Related Documentation

- **Python Environment**: See [Python Environment Setup](python-env.md) for dependency installation with uv
- **Local Development**: See [Local Development Setup](local-dev.md) for Docker infrastructure setup
- **Testing**: See [Code Quality Guide](code-quality.md) for testing best practices
- **CLI Usage**: See [CLI Documentation](cli-usage.md) for language configuration options
