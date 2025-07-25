# Shepherd Pipeline Spec

## Overview

This document defines the architectural blueprint for Shepherd's AI-powered transcription and summarization pipeline system using Prefect. The current implementation focuses on YouTube video processing with robust local development and flexible deployment architecture.

## Development & Deployment Environment

### Development Tooling

1. **pyenv** for Python version management (Python 3.12+)
2. **uv** for fast dependency management and virtual environments
3. **Docker Compose** for local infrastructure (Prefect server, PostgreSQL, worker)

### Local Dev & Testing

1. **Container-Based Infrastructure**: Docker Compose provides Prefect server, PostgreSQL database, and worker containers
2. **Mock-First Development**: All external APIs (YouTube, Mistral, OpenAI) have comprehensive mock implementations
3. **Environment Toggle**: Switch between mock and production APIs via CLI flags and configuration
4. **Real-time UI**: Prefect UI accessible at `http://localhost:4200` for pipeline monitoring

### Deployment Architecture

1. **Stateless Design**: All pipeline code is stateless with configuration via environment variables
2. **Kubernetes Ready**: Designed for future Kubernetes deployment with Prefect Cloud integration
3. **Multi-Provider Support**: Flexible AI model selection across OpenAI and Mistral providers

## Current Pipeline Implementation

### Implemented Entry Points

**✅ YouTube Video Pipeline (Production Ready)**
- Download (yt-dlp) → Extract Audio → Chunk Audio → Transcribe → Chinese Translation → Text Correction → Summarization
- **Features**:
  - Time range extraction (`youtube_start_time`, `youtube_end_time`)
  - Multi-provider AI support (OpenAI, Mistral)
  - Traditional Chinese processing with OpenCC
  - Artifact caching and resumption
  - Rich CLI with export capabilities
  - Comprehensive error handling and retries

### Planned Entry Points

**🚧 Audio File Pipeline (Architecture Defined)**
- Upload → Chunk Audio → Transcribe → (Translate/Correct) → Summarize
- Model selection configurable at each step

**🚧 Text Summary Pipeline (Architecture Defined)**
- Accept Transcript → Summarize with custom instructions, model, and word limits
- Direct text processing without audio components

### Pipeline Design Principles

**Modular Tasks**: Each processing step is an independent, retryable Prefect task:
- `download_youtube_audio()` - yt-dlp integration with time ranges
- `chunk_audio()` - Audio segmentation using pydub
- `transcribe_audio_chunk()` - Multi-provider transcription with fallbacks
- `correct_transcription()` - AI-powered text correction
- `summarize_text()` - Configurable summarization with custom instructions

**Runtime Configuration**: All model selection and parameters configurable per job:
```python
PipelineInput(
    youtube_url="https://youtube.com/watch?v=...",
    youtube_start_time=30,
    youtube_end_time=90,
    transcription_model="voxtral-mini-latest",
    correction_model="gpt-4o-mini",
    summarization_model="mistral-small-latest",
    target_language="zh-TW"
)
```
