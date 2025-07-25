# Shepard Pipeline

A Prefect-powered AI transcription and summarization system that transforms audio and video content into structured insights through configurable AI workflows.

## AI-Enabled Architecture

**Intelligent Processing Chain**: YouTube videos and audio files flow through an AI-powered pipeline:
1. **Content Ingestion** → Automated download and audio extraction
2. **Speech-to-Text** → AI transcription with language detection
3. **Content Enhancement** → AI-powered text correction and translation
4. **Summarization** → Configurable AI summarization with custom instructions

**Adaptive AI Integration**: Runtime model selection for transcription (Voxtral) and summarization (OpenAI GPT-4), with flexible prompt engineering and parameter tuning per job.

## Features

- **Modular AI Pipeline**: Each AI processing step is an independent Prefect task with configurable models
- **Mock-First Development**: All AI services (transcription, summarization) mocked for rapid local development
- **Runtime AI Configuration**: Dynamic model selection, prompt customization, and parameter tuning
- **Type-Safe AI Workflows**: Full type validation for AI inputs/outputs with Pydantic schemas

## Quick Start

### Prerequisites

1. **Install pyenv for Python version management:**
   ```bash
   # macOS
   brew install pyenv

   # Linux/Unix
   curl -fsSL https://pyenv.run | bash
   ```

2. **Configure your shell (add to ~/.bashrc, ~/.zshrc, etc.):**
   ```bash
   export PYENV_ROOT="$HOME/.pyenv"
   [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
   eval "$(pyenv init -)"
   ```

3. **Restart your shell:**
   ```bash
   exec "$SHELL"
   ```

4. **Install and set Python version:**
   ```bash
   pyenv install 3.12
   pyenv local 3.12
   ```

5. **Install uv:**
   ```bash
   # Install via pipx or pip
   pip install uv
   ```

### Setup and Run

```bash
# Install dependencies
uv sync

# Set up pre-commit hooks
uv run pre-commit install

# Copy environment file
cp .env.example .env

# Start Prefect server
uv run prefect server start

# Run demo pipeline
uv run python -m shepard_pipeline.demo
```

## Project Structure

```
shepard_pipeline/
├── flows/           # Prefect flow definitions
├── tasks/           # Individual Prefect tasks
├── models/          # Pydantic models and schemas
├── services/        # External service integrations (mocked)
├── config/          # Configuration management
└── cli/             # Command-line interface
```

## Development

See [local-dev.md](../llm-docs/local-dev.md) for detailed development setup.
