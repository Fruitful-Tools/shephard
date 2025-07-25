# Code Quality Guide

This document outlines the code quality tools, standards, and practices used in the Shepard Pipeline project.

## Overview

We use modern, cutting-edge tools to maintain high code quality with extreme performance:

- **[Ruff](https://docs.astral.sh/ruff/) v0.12.5**: Ultra-fast Rust-based Python linter and formatter that consolidates 10+ traditional tools (Black, isort, flake8, Pylint, pydocstyle, etc.) with 150-200x speed improvement
- **[mypy](https://mypy.readthedocs.io/)**: Static type checker for Python with strict configuration
- **[typos](https://github.com/crate-ci/typos) v1.24.6**: Lightning-fast spell checker for source code written in Rust
- **[pytest](https://docs.pytest.org/)**: Modern testing framework with comprehensive configuration
- **[pre-commit](https://pre-commit.com/) v4.6.0**: Git hooks framework with latest hook versions for automated quality checks

This modern stack represents the **2024 state-of-the-art** for Python development, prioritizing performance and developer experience.

## Tools Configuration

### Ruff

Ruff is configured in `pyproject.toml` and serves multiple purposes:

#### As a Linter (2024 Configuration)
Ruff consolidates multiple traditional tools with **gradual rule adoption**:

**Essential Rules (Always Enabled)**:
- **pycodestyle** (E): PEP 8 style violations
- **Pyflakes** (F): Logical errors and unused imports

**Extended Rules (Progressively Added)**:
- **isort** (I): Import sorting and organization
- **pyupgrade** (UP): Automatic upgrades to newer Python syntax
- **flake8-bugbear** (B): Common bug patterns and anti-patterns
- **flake8-comprehensions** (C4): List/dict comprehension improvements
- **flake8-simplify** (SIM): Code simplification suggestions
- **flake8-unused-arguments** (ARG): Unused function arguments
- **flake8-use-pathlib** (PTH): Prefer pathlib over os.path
- **flake8-quotes** (Q): Consistent quote style
- **flake8-annotations** (ANN): Type annotations
- **flake8-type-checking** (TCH): Type checking imports

**Auto-Fixing Enabled** for safe transformations:
- F401: Remove unused imports
- I001: Import sorting
- UP017: datetime.timezone.utc upgrades
- C4: Comprehension improvements
- SIM: Safe simplifications

#### As a Formatter (2024 Features)
Ruff formats code with advanced features:
- **88 character line length** (Black-compatible)
- **Double quotes** for strings
- **Space-based indentation** (4 spaces)
- **Docstring code formatting**: Formats code blocks in docstrings
- **Configurable docstring line length**: 72 characters for better readability
- **Automatic trailing comma handling**
- **Cross-platform line endings**: Auto-detects and normalizes

#### Usage (Latest Commands)
```bash
# Modern workflow - lint with auto-fix then format
uv run ruff check --fix .
uv run ruff format .

# Check without fixing (for CI/review)
uv run ruff check .

# Check specific files
uv run ruff check shepard_pipeline/models.py

# Show rule explanations
uv run ruff rule E501

# Preview upcoming changes (safe)
uv run ruff check --diff .
uv run ruff format --diff .

# Performance: check only changed files
git diff --name-only | xargs uv run ruff check
```

### mypy

Static type checking ensures type safety and catches errors early.

#### Configuration
- Strict mode enabled
- Requires type annotations for all functions
- Checks for unreachable code and unused imports
- Validates return types and parameter types

#### Usage
```bash
# Type check entire project
uv run mypy .

# Check specific module
uv run mypy shepard_pipeline/

# Check with verbose output
uv run mypy --verbose shepard_pipeline/
```

### typos v1.24.6

Lightning-fast Rust-based spell checker that catches typos in code, comments, and documentation with **superior performance**.

#### Configuration (`.typos.toml`)
Our configuration includes:
- **Smart pattern exclusions**: Ignores hex patterns, base64 strings, and common false positives
- **Project-specific dictionary**: Custom words like "shepard", "prefect", "pydantic"
- **File type targeting**: Focuses on `.py`, `.md`, `.toml`, `.yaml` files
- **Performance optimizations**: Excludes lock files, build artifacts, and dependencies

#### Usage (Latest Commands)
```bash
# Check for typos (extremely fast)
uv run typos

# Check with detailed output
uv run typos --verbose

# Fix typos automatically (use with caution in CI)
uv run typos --write-changes

# Check specific files
uv run typos README.md shepard_pipeline/

# Dry run to preview changes
uv run typos --dry-run --write-changes

# Custom configuration file
uv run typos --config custom.typos.toml
```

### pytest

Testing framework with extensive configuration for different test types.

#### Test Organization
- **Unit tests**: Fast, isolated tests in `tests/unit/`
- **Integration tests**: End-to-end tests in `tests/integration/`
- **Slow tests**: Marked with `@pytest.mark.slow`

#### Usage
```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/unit/

# Run with coverage
uv run pytest --cov=shepard_pipeline

# Run fast tests only
uv run pytest -m "not slow"

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with verbose output
uv run pytest -v
```

### pre-commit

Automated quality checks run before each commit.

#### Hooks Configured
1. **Basic checks**: trailing whitespace, file endings, YAML syntax
2. **Ruff linting**: automatic fixes applied
3. **Ruff formatting**: code formatting
4. **typos**: spell checking
5. **mypy**: type checking

#### Usage
```bash
# Install hooks (one-time setup)
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff

# Skip hooks for urgent commits (not recommended)
git commit --no-verify -m "urgent fix"

# Update hook versions
uv run pre-commit autoupdate
```

## Development Workflow

### Before Starting Work
```bash
# Ensure tools are installed
uv sync
uv run pre-commit install
```

### During Development
```bash
# Check code quality frequently
uv run ruff check --fix .
uv run mypy .

# Run relevant tests
uv run pytest tests/unit/test_models.py
```

### Before Committing
```bash
# Essential workflow for fixing pre-commit issues:
# 1. Always add files to git first (pre-commit needs staged files)
git add -A

# 2. Run format first (fixes most formatting issues)
uv run ruff format .

# 3. Run linting with auto-fix (fixes imports, unused vars, etc.)
uv run ruff check --fix .

# 4. Fix any remaining typing issues manually, then run mypy
uv run mypy .

# 5. Run all pre-commit checks
uv run pre-commit run --all-files

# 6. If pre-commit made changes, add them and run again
git add -A
uv run pre-commit run --all-files

# Run tests to ensure functionality
uv run pytest
```

The pre-commit hooks will automatically run these checks, but running them manually helps catch issues early.

**Important**: Always run `git add -A` before pre-commit checks, as pre-commit only works on staged files.

## Code Standards

### Python Style Guide

We follow PEP 8 with these specific guidelines:

#### Line Length
- **88 characters maximum** (Black/Ruff default)
- Break long lines at logical points
- Use parentheses for line continuations

#### Imports
```python
# Standard library imports first
import asyncio
import logging
from pathlib import Path

# Third-party imports second
import httpx
from pydantic import BaseModel
from prefect import task

# Local imports last
from shepard_pipeline.models import JobStatus
from shepard_pipeline.services import TranscriptionService
```

#### Type Annotations
```python
# Always use type annotations
def process_audio(file_path: Path, chunk_size: int = 60) -> list[str]:
    """Process audio file into chunks."""
    return []

# Use modern union syntax (Python 3.10+)
def get_result() -> str | None:
    return None

# Use generic types
from collections.abc import Sequence

def process_items(items: Sequence[str]) -> list[str]:
    return list(items)
```

#### Error Handling
```python
# Use specific exception types
try:
    result = api_call()
except httpx.RequestError as e:
    logger.error(f"API request failed: {e}")
    raise
except Exception:
    logger.exception("Unexpected error in API call")
    raise
```

#### Docstrings
```python
def transcribe_audio(audio_path: Path, language: str = "zh-TW") -> str:
    """Transcribe audio file to text.

    Args:
        audio_path: Path to the audio file
        language: Language code for transcription

    Returns:
        Transcribed text

    Raises:
        FileNotFoundError: If audio file doesn't exist
        TranscriptionError: If transcription fails
    """
    return ""
```

### Configuration Files

#### Keep Configuration Consistent
- Use `pyproject.toml` for tool configuration when possible
- Keep line lengths and style consistent across all tools
- Document any deviations from defaults

#### Environment Variables
```python
# Use pydantic-settings for configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"
```

## Troubleshooting

### Common Issues

#### Ruff vs Black Compatibility
Ruff is configured to be Black-compatible, but if you encounter formatting differences:
```bash
# Check ruff formatting
uv run ruff format --diff

# Apply ruff formatting
uv run ruff format
```

#### mypy Type Errors
```bash
# Common fixes:
# 1. Add type annotations
def process_item(item):  # ❌
def process_item(item: str) -> str:  # ✅

# 2. Use proper imports for typing
from typing import Any, Optional  # ❌ (deprecated)
from collections.abc import Sequence  # ✅
```

#### Pre-commit Hook Failures
```bash
# If hooks fail, follow the systematic approach:

# 1. Always stage files first
git add -A

# 2. Run tools in order:
uv run ruff format .         # Fix formatting first
uv run ruff check --fix .    # Fix linting issues
uv run mypy .               # Check types manually

# 3. Run specific hooks to isolate issues:
uv run pre-commit run ruff-format --all-files
uv run pre-commit run ruff-check --all-files
uv run pre-commit run mypy --all-files

# 4. After fixes, stage and retry:
git add -A
uv run pre-commit run --all-files

# Common fixes needed:
# - Add type annotations for missing ANN001/ANN201 errors
# - Replace Optional[X] with X | None (UP045 errors)
# - Mark unused arguments with underscore prefix (ARG001/ARG002)
# - Use # noqa: ANN401 for necessary **kwargs: Any usage
```

#### Performance Issues
```bash
# If tools are slow, check file exclusions:
# 1. Ensure .venv is excluded
# 2. Check for large generated files
# 3. Use file-specific commands for faster feedback:
uv run ruff check specific_file.py
```

## Integration with IDEs

### VS Code
Install these extensions:
- **Ruff**: Official Ruff extension
- **Python**: Microsoft Python extension
- **mypy**: Mypy type checker

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": false,  // Disable built-in linting
    "ruff.enable": true,
    "ruff.organizeImports": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true,
        "source.fixAll": true
    },
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

### PyCharm/IntelliJ
1. Install the Ruff plugin
2. Configure Python interpreter to use `.venv/bin/python`
3. Enable "Optimize imports on the fly"
4. Set up external tools for manual runs:
   - Tool: `uv`
   - Arguments: `run ruff check --fix .`

## Continuous Integration

### GitHub Actions
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run ruff
        run: uv run ruff check .
      - name: Run mypy
        run: uv run mypy .
      - name: Run tests
        run: uv run pytest
      - name: Check typos
        run: uv run typos
```

## Migration Guide

### From Old Tools to Ruff

If you're coming from the previous setup (Black + isort + flake8):

#### 1. Update Dependencies
```bash
# Remove old tools (already done in pyproject.toml)
# black, isort, flake8 -> ruff

# Install new dependencies
uv sync
```

#### 2. Update Commands
```bash
# Old workflow:
black .
isort .
flake8 .

# New workflow:
uv run ruff format    # replaces black
uv run ruff check --fix  # replaces isort + flake8
```

#### 3. Update CI/CD
Replace multiple tool commands with single ruff commands for faster CI runs.

#### 4. IDE Configuration
Update IDE settings to use ruff instead of separate tools.

## Best Practices

### Daily Development
1. **Run tools frequently**: Don't wait until commit time
2. **Fix issues immediately**: Don't accumulate quality debt
3. **Use IDE integration**: Get immediate feedback while coding
4. **Write tests first**: TDD helps with better type annotations

### Code Reviews
1. **Focus on logic**: Let tools handle style
2. **Check test coverage**: Ensure new code is tested
3. **Verify type annotations**: Ensure proper typing
4. **Review performance**: Check for obvious inefficiencies

### Maintenance
1. **Update tools regularly**: Keep dependencies current
2. **Review configurations**: Adjust rules as project evolves
3. **Monitor CI performance**: Optimize for faster feedback
4. **Document exceptions**: Explain any rule overrides

## Lessons Learned & Best Practices

### Pre-commit Workflow Improvements

Based on experience fixing code quality issues, here are key improvements made to the workflow:

#### 1. **Systematic Issue Resolution Order**
Always follow this sequence when fixing pre-commit failures:
1. `git add -A` (stage all files - pre-commit only works on staged files)
2. `uv run ruff format .` (fix formatting first)
3. `uv run ruff check --fix .` (fix linting issues)
4. Fix remaining typing issues manually
5. `uv run mypy .` (verify type checking)
6. `uv run pre-commit run --all-files` (run all checks)

#### 2. **Common Type Annotation Patterns**
- **Modern Union Syntax**: Use `X | None` instead of `Optional[X]`
- **Modern Collection Types**: Use `dict`, `list` instead of `Dict`, `List`
- **Unused Arguments**: Prefix with underscore (`_text`) instead of removing
- **Flexible kwargs**: Use `# noqa: ANN401` for legitimate `**kwargs: Any` usage

#### 3. **MyPy Configuration for Tests**
Added test-specific overrides in `pyproject.toml`:
```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_decorators = false
warn_no_return = false
```

#### 4. **Pre-commit Configuration Adjustments**
- Removed `--strict` flag from mypy pre-commit hook to use pyproject.toml config
- Maintained strict typing for main code while relaxing rules for tests

### Future Prevention Strategies

1. **IDE Integration**: Configure your editor to show ruff and mypy errors in real-time
2. **Frequent Checks**: Run `uv run ruff format . && uv run ruff check --fix .` frequently during development
3. **Type-First Development**: Add type annotations as you write code, not after
4. **Test Type Safety**: Use proper typing in test fixtures to catch issues early

This comprehensive code quality setup ensures consistent, readable, and maintainable code across the entire Shepard Pipeline project.
