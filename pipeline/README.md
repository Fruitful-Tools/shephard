[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

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

## Context Engineering

This repository implements context engineering prompts by [suggestion from this repo](https://github.com/coleam00/context-engineering-intro).

### What is Context Engineering?

Context Engineering represents a paradigm shift from traditional prompt engineering:

### Prompt Engineering vs Context Engineering

**Prompt Engineering:**
- Focuses on clever wording and specific phrasing
- Limited to how you phrase a task
- Like giving someone a sticky note

**Context Engineering:**
- A complete system for providing comprehensive context
- Includes documentation, examples, rules, patterns, and validation
- Like writing a full screenplay with all the details

### Why Context Engineering Matters

1. **Reduces AI Failures**: Most agent failures aren't model failures - they're context failures
2. **Ensures Consistency**: AI follows your project patterns and conventions
3. **Enables Complex Features**: AI can handle multi-step implementations with proper context
4. **Self-Correcting**: Validation loops allow AI to fix its own mistakes

### Shepherd Pipeline Context Engineering Structure

```
shepherd_pipeline/
├── CLAUDE.md                    # AI agent guidance and development workflows
├── llms.txt                     # Primary project overview and entry point
└── llm-docs/
    ├── PRPs/
    │   ├── templates/
    │   │   ├── PRP_base.md      # Comprehensive feature implementation template
    │   │   └── PRP_example.md   # Example PRP with Shepherd Pipeline context
    │   └── [generated_prps]/    # Project-specific PRPs for complex features
    ├── python-env.md            # Environment setup and tooling
    ├── local-dev.md             # Development infrastructure
    ├── project-spec.md          # Architectural blueprint
    ├── model-configuration.md   # AI service integration patterns
    ├── chinese-translation.md   # Specialized language processing
    └── artifact-system.md       # Caching and deduplication patterns
```

### Key Context Engineering Components

1. **CLAUDE.md**: Provides AI agents with essential commands, workflows, and project-specific patterns
2. **llms.txt**: Serves as the primary entry point with comprehensive project overview
3. **PRP Templates**: Problem-Requirements-Plan templates for complex feature implementation
4. **Specialized Documentation**: Domain-specific guides for Chinese processing, AI integration, etc.

This context engineering approach enables AI agents to understand the Shepherd Pipeline's architecture, follow established patterns, and implement features with minimal guidance while maintaining code quality and consistency.

### Step-by-Step Guide

#### 1. Create Your Initial Feature Request

create UCS-XXXXX.md initial prp file, refer to `prp_example.md` as an example format, or simply copy from JIRA if ticket is well written.

#### 2. Generate the PRP

PRPs (Product Requirements Prompts) are comprehensive implementation blueprints that include:

- Complete context and documentation
- Implementation steps with validation
- Error handling patterns
- Test requirements

They are similar to PRDs (Product Requirements Documents) but are crafted more specifically to instruct an AI coding assistant.

Run in Claude Code:
```bash
/generate-prp feat-XXXXX.md
```

**Note:** The slash commands are custom commands defined in `.claude/commands/`. You can view their implementation:
- `.claude/commands/generate-prp.md` - See how it researches and creates PRPs
- `.claude/commands/execute-prp.md` - See how it implements features from PRPs

The `$ARGUMENTS` variable in these commands receives whatever you pass after the command name (e.g., `INITIAL.md` or `PRPs/your-feature.md`).

This command will:

- Read your feature request
- Research the codebase for patterns
- Search for relevant documentation
- Create a comprehensive PRP in `llm-docs/PRPs/your-feature-name.md`

#### 3. Execute the PRP

Once generated, execute the PRP to implement your feature:

```bash
/execute-prp llm-docs/PRPs/your-feature-name.md
```

The AI coding assistant will:
1. Read all context from the PRP
2. Create a detailed implementation plan
3. Execute each step with validation
4. Run tests and fix any issues
5. Ensure all success criteria are met
